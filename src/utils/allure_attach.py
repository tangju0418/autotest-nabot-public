"""Allure 报告附件辅助。"""
from __future__ import annotations

import json
import shlex
from typing import Any, Dict, Mapping, Optional

import allure
from allure_commons.types import AttachmentType

from src.utils.http_client import HTTPClient, resolve_api_headers


def attach_request_method_and_url(
    method: str,
    endpoint: str,
    *,
    client: Optional[HTTPClient] = None,
) -> None:
    """
    附加「METHOD 完整URL」文本附件, 须在「请求参数」等附件之前调用以符合报告阅读顺序。
    method 建议取自对应 API 封装类上的 HTTP_METHOD_* 常量, 与真实请求动词一致。
    """
    c = client if client is not None else HTTPClient()
    full_url = c._build_url(endpoint)
    line = f"{method.upper()} {full_url}"
    allure.attach(line, "请求方法及URL", attachment_type=allure.attachment_type.TEXT)


def _redact_header_value(name: str, value: str) -> str:
    key = name.lower()
    if key in ("authorization", "proxy-authorization"):
        parts = value.split(None, 1)
        if len(parts) == 2 and parts[0].lower() in ("bearer", "token", "basic", "digest"):
            return f"{parts[0]} ***"
        return "***"
    if key in ("cookie", "set-cookie", "x-api-key", "api-key"):
        return "***"
    return value


def redact_headers(headers: Optional[Mapping[str, Any]]) -> Dict[str, str]:
    """返回脱敏后的请求头字典(用于展示与 curl)。"""
    if not headers:
        return {}
    return {str(k): _redact_header_value(str(k), str(v)) for k, v in headers.items()}


def attach_request_headers_redacted(
    headers: Optional[Mapping[str, Any]],
    *,
    include_default_json_content_type: bool = False,
) -> None:
    """在「请求方法及URL」之后附加「请求头(脱敏)」。"""
    merged: Dict[str, Any] = dict(headers or {})
    if include_default_json_content_type:
        merged.setdefault("Content-Type", "application/json")
    redacted = {str(k): _redact_header_value(str(k), str(v)) for k, v in merged.items()}
    text = json.dumps(redacted, ensure_ascii=False, indent=2)
    allure.attach(text, "请求头(脱敏)", attachment_type=allure.attachment_type.JSON)


def attach_request_json_body(body: Any, name: str = "请求参数") -> None:
    """附加与 HTTP 请求体一致的 JSON(dict/list 会序列化)。"""
    if isinstance(body, (dict, list)):
        text = json.dumps(body, ensure_ascii=False, indent=2)
    else:
        text = str(body)
    allure.attach(text, name, attachment_type=allure.attachment_type.JSON)


def build_redacted_curl(
    method: str,
    full_url: str,
    headers: Optional[Mapping[str, Any]],
    json_body: Any,
    *,
    include_request_body: bool = True,
) -> str:
    """
    生成可在 bash/zsh 中复制的 curl; 头脱敏。
    include_request_body=False 时适用于 GET/HEAD 等无 body。
    """
    lines = [f"curl -X {method.upper()} {shlex.quote(full_url)}"]
    merged: Dict[str, str] = {}
    if headers:
        for k, v in headers.items():
            merged[str(k)] = str(v)
    if include_request_body:
        merged.setdefault("Content-Type", "application/json")
    for k, v in redact_headers(merged).items():
        lines.append(f"  -H {shlex.quote(f'{k}: {v}')}")
    if include_request_body:
        if isinstance(json_body, (dict, list)):
            raw = json.dumps(json_body, ensure_ascii=False, separators=(",", ":"))
        else:
            raw = str(json_body)
        lines.append(f"  --data-raw {shlex.quote(raw)}")
    lines.append("  --compressed")
    return " \\\n".join(lines)


def _curl_copy_html_page(cmd: str) -> str:
    """内嵌复制按钮的独立 HTML, 供 Allure 以 HTML 附件展示。"""
    js_literal = json.dumps(cmd, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>curl</title>
</head>
<body style="font-family:system-ui,sans-serif;padding:12px;margin:0;">
<button type="button" id="copy-btn" style="padding:8px 12px;cursor:pointer;margin-bottom:10px;">复制 curl 到剪贴板</button>
<pre id="curl-pre" style="white-space:pre-wrap;word-break:break-all;background:#f6f8fa;padding:12px;border-radius:6px;font-size:12px;line-height:1.4;margin:0;"></pre>
<p id="hint" style="color:#666;font-size:12px;margin-top:8px;display:none;">若按钮无效, 请手动选中上方命令复制。</p>
<script>
(function() {{
  var text = {js_literal};
  var pre = document.getElementById('curl-pre');
  var btn = document.getElementById('copy-btn');
  var hint = document.getElementById('hint');
  pre.textContent = text;
  function done() {{
    var prev = btn.textContent;
    btn.textContent = '已复制';
    setTimeout(function() {{ btn.textContent = prev; }}, 2000);
  }}
  function showHint() {{ hint.style.display = 'block'; }}
  btn.addEventListener('click', function() {{
    if (navigator.clipboard && window.isSecureContext) {{
      navigator.clipboard.writeText(text).then(done).catch(function() {{ fallback(); }});
    }} else {{
      fallback();
    }}
    function fallback() {{
      try {{
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.style.position = 'fixed';
        ta.style.left = '-9999px';
        document.body.appendChild(ta);
        ta.select();
        var ok = document.execCommand('copy');
        document.body.removeChild(ta);
        if (ok) done(); else showHint();
      }} catch (e) {{ showHint(); }}
    }}
  }});
}})();
</script>
</body>
</html>"""


def attach_redacted_curl(
    method: str,
    endpoint: str,
    headers: Optional[Mapping[str, Any]],
    json_body: Any,
    *,
    include_request_body: bool = True,
    client: Optional[HTTPClient] = None,
) -> None:
    """在「请求参数」之后附加带复制按钮的脱敏 curl。"""
    c = client if client is not None else HTTPClient()
    full_url = c._build_url(endpoint)
    cmd = build_redacted_curl(
        method,
        full_url,
        headers,
        json_body,
        include_request_body=include_request_body,
    )
    allure.attach(
        _curl_copy_html_page(cmd),
        "curl 复现(脱敏, bash/zsh)",
        attachment_type=AttachmentType.HTML,
    )


def attach_allure_request_prepare_bundle(
    method: str,
    endpoint: str,
    raw_headers: Optional[Mapping[str, Any]],
    *,
    json_body: Any = None,
    include_request_body: bool = True,
    client: Optional[HTTPClient] = None,
    use_env_token: bool = True,
) -> None:
    """
    「准备测试数据」步骤内统一顺序: 请求方法及URL -> 请求头(脱敏) -> 请求参数 -> curl(脱敏)。
    GET 等无 body 时设 include_request_body=False, 请求参数附件为 {}。
    """
    headers_for_report = resolve_api_headers(
        dict(raw_headers) if raw_headers else None,
        use_env_token=use_env_token,
    )
    attach_request_method_and_url(method, endpoint, client=client)
    attach_request_headers_redacted(
        headers_for_report,
        include_default_json_content_type=False,
    )
    body_attach: Any = json_body if include_request_body else {}
    attach_request_json_body(body_attach)
    attach_redacted_curl(
        method,
        endpoint,
        headers_for_report,
        json_body if include_request_body else None,
        include_request_body=include_request_body,
        client=client,
    )
