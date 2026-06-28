[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Folder,

    [string]$Session = "wechat-batch",

    [string]$Token = "1740056467"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$folderPath = (Resolve-Path -LiteralPath $Folder).Path
$assetDir = Join-Path $folderPath ".codex_wechat"
$payloadPath = Join-Path $assetDir "payload.json"
$uploadListPath = Join-Path $assetDir "upload_reverse.json"
$renderPath = Join-Path $assetDir "render_body.js"

foreach ($required in @($payloadPath, $uploadListPath, $renderPath)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Missing required file: $required"
    }
}

$payload = Get-Content -Raw -Encoding UTF8 -LiteralPath $payloadPath | ConvertFrom-Json
$uploadList = Get-Content -Raw -Encoding UTF8 -LiteralPath $uploadListPath | ConvertFrom-Json
$coverFileName = if ($payload.cover_path) { [System.IO.Path]::GetFileName([string]$payload.cover_path) } else { "" }

function Invoke-AgentBrowser {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )
    & npx.cmd --yes agent-browser --session $Session @Args
    if ($LASTEXITCODE -ne 0) {
        throw "agent-browser failed: $($Args -join ' ')"
    }
}

function Invoke-AgentBrowserEval {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Script
    )
    $tmp = Join-Path $env:TEMP ("codex-wechat-eval-" + [guid]::NewGuid().ToString() + ".js")
    Set-Content -LiteralPath $tmp -Value $Script -Encoding UTF8
    try {
        Get-Content -Raw -Encoding UTF8 -LiteralPath $tmp | & npx.cmd --yes agent-browser --session $Session eval --stdin
        if ($LASTEXITCODE -ne 0) {
            throw "agent-browser eval failed"
        }
    } finally {
        Remove-Item -LiteralPath $tmp -ErrorAction SilentlyContinue
    }
}

function Wait-Millis {
    param([int]$Ms)
    Invoke-AgentBrowser @("wait", "$Ms")
}

function Click-VisiblePrimaryButton {
    $clickScript = @"
(() => {
  const nodes = Array.from(document.querySelectorAll('button.weui-desktop-btn_primary, .weui-desktop-btn_primary'))
    .map(el => ({ el, rect: el.getBoundingClientRect(), text: (el.innerText || '').trim() }))
    .filter(x => x.rect.width > 0 && x.rect.height > 0)
    .sort((a, b) => (b.rect.top - a.rect.top) || (a.rect.left - b.rect.left));
  const node = nodes[0]?.el;
  if (!node) throw new Error('primary button not found');
  node.click();
  return (node.innerText || '').trim();
})()
"@
    Invoke-AgentBrowserEval -Script $clickScript
}

function Get-VisibleDialogTitle {
    $script = @"
(() => {
  const titles = Array.from(document.querySelectorAll('h3, .weui-desktop-dialog__hd, .dialog_hd, .weui-desktop-dialog__title'))
    .map(el => ({ text: (el.innerText || '').trim(), rect: el.getBoundingClientRect() }))
    .filter(x => x.text && x.rect.width > 0 && x.rect.height > 0)
    .sort((a, b) => a.rect.top - b.rect.top);
  return titles[0]?.text || '';
})()
"@
    Invoke-AgentBrowserEval -Script $script
}

function Complete-CoverDialogFlow {
    $stateScript = @"
(() => {
  const chooseTitle = '\u9009\u62e9\u56fe\u7247';
  const editTitle = '\u7f16\u8f91\u5c01\u9762';
  const saveDraftText = '\u4fdd\u5b58\u4e3a\u8349\u7a3f';
  const saveText = '\u4fdd\u5b58';
  const titleNodes = Array.from(document.querySelectorAll('h3, .weui-desktop-dialog__hd, .dialog_hd, .weui-desktop-dialog__title'))
    .map(el => ({ text: (el.innerText || '').trim(), rect: el.getBoundingClientRect() }))
    .filter(x => x.text && x.rect.width > 0 && x.rect.height > 0)
    .sort((a, b) => a.rect.top - b.rect.top);
  const title = titleNodes[0]?.text || '';

  const primaryButtons = Array.from(document.querySelectorAll('button.weui-desktop-btn_primary, .weui-desktop-btn_primary'))
    .map(el => ({ el, text: (el.innerText || '').trim(), rect: el.getBoundingClientRect() }))
    .filter(x => x.rect.width > 0 && x.rect.height > 0);
  const visiblePrimaryTexts = primaryButtons.map(x => x.text);
  const visibleActions = Array.from(document.querySelectorAll('button, a, [role="button"], .weui-desktop-btn'))
    .map(el => ({ el, text: (el.innerText || '').trim(), rect: el.getBoundingClientRect() }))
    .filter(x => x.text && x.rect.width > 0 && x.rect.height > 0);
  const visibleActionTexts = visibleActions.map(x => x.text);

  const isSaveButton = (text) => text.includes(saveDraftText) || text === saveText;
  const saveButton = visibleActions.find(x => isSaveButton(x.text));
  const dialogButton = primaryButtons
    .filter(x => !isSaveButton(x.text))
    .sort((a, b) => (b.rect.top - a.rect.top) || (b.rect.left - a.rect.left))[0];

  if (title.includes(chooseTitle)) {
    if (!dialogButton) throw new Error('next button not found in choose image dialog');
    dialogButton.el.click();
    return JSON.stringify({ step: 'dialog-next', title, button: dialogButton.text, primaryButtons: visiblePrimaryTexts, actions: visibleActionTexts });
  }

  if (title.includes(editTitle)) {
    if (!dialogButton) throw new Error('confirm button not found in edit cover dialog');
    dialogButton.el.click();
    return JSON.stringify({ step: 'dialog-confirm', title, button: dialogButton.text, primaryButtons: visiblePrimaryTexts, actions: visibleActionTexts });
  }

  if (title && dialogButton) {
    dialogButton.el.click();
    return JSON.stringify({ step: 'dialog-fallback', title, button: dialogButton.text, primaryButtons: visiblePrimaryTexts, actions: visibleActionTexts });
  }

  if (saveButton) {
    saveButton.el.click();
    return JSON.stringify({ step: 'save-draft', title, button: saveButton.text, primaryButtons: visiblePrimaryTexts, actions: visibleActionTexts });
  }

  return JSON.stringify({ step: 'idle', title, button: '', primaryButtons: visiblePrimaryTexts, actions: visibleActionTexts });
})()
"@

    $first = Invoke-AgentBrowserEval -Script $stateScript
    Write-Host $first
    Wait-Millis -Ms 1800

    $second = Invoke-AgentBrowserEval -Script $stateScript
    Write-Host $second
    Wait-Millis -Ms 2500

    $third = Invoke-AgentBrowserEval -Script $stateScript
    Write-Host $third
    return $third
}

function Decode-AsciiUnicode {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Escaped
    )
    return [System.Text.RegularExpressions.Regex]::Unescape($Escaped)
}

$textManualSave = Decode-AsciiUnicode '\u624b\u52a8\u4fdd\u5b58'
$textSaved = Decode-AsciiUnicode '\u5df2\u4fdd\u5b58'

$editorUrl = "https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=77&createType=0&token=$Token&lang=zh_CN"
$navScript = @"
(() => {
  location.href = '$editorUrl';
  return 'navigating';
})()
"@
Invoke-AgentBrowserEval -Script $navScript
Invoke-AgentBrowser @("wait", "--load", "networkidle")

foreach ($img in $uploadList) {
    Invoke-AgentBrowser @("upload", "input[type=file]", [string]$img)
    Wait-Millis -Ms 1500
}

Get-Content -Raw -Encoding UTF8 -LiteralPath $renderPath | & npx.cmd --yes agent-browser --session $Session eval --stdin
if ($LASTEXITCODE -ne 0) {
    throw "render_body.js execution failed"
}
Wait-Millis -Ms 1000

$openLibraryScript = @"
(() => {
  const btn = document.querySelector('#js_cover_description_area .js_imagedialog');
  if (!btn) throw new Error('cover image library button not found');
  btn.click();
  return 'opened image dialog';
})()
"@
Invoke-AgentBrowserEval -Script $openLibraryScript
Wait-Millis -Ms 1500

$selectCoverScript = @"
(() => {
  const targetName = $(ConvertTo-Json -Compress -InputObject $coverFileName);
  const candidates = Array.from(document.querySelectorAll('*'))
    .map(el => ({
      el,
      txt: (el.innerText || '').trim(),
      rect: el.getBoundingClientRect()
    }))
    .filter(x => x.txt.endsWith('.png') && !x.txt.includes('\n') && x.rect.width > 0 && x.rect.height > 0)
    .sort((a, b) => (a.rect.top - b.rect.top) || (a.rect.left - b.rect.left));
  const exact = candidates.find(x => x.txt === targetName);
  const target = (exact || candidates[0])?.el;
  if (!target) throw new Error('cover image item not found in recent list');
  target.click();
  return (target.innerText || '').trim();
})()
"@
Invoke-AgentBrowserEval -Script $selectCoverScript
Wait-Millis -Ms 1000

$coverFlowResult = Complete-CoverDialogFlow
Wait-Millis -Ms 2500

$verifyScript = @"
(() => {
  const text = document.body.innerText || '';
  return JSON.stringify({
    title: document.querySelectorAll('.ProseMirror')[0]?.innerText || '',
    hasSavedHint: text.includes($(ConvertTo-Json -Compress -InputObject $textManualSave)) || text.includes($(ConvertTo-Json -Compress -InputObject $textSaved)),
    coverPreview: getComputedStyle(document.querySelector('.js_cover_preview_new')).backgroundImage,
    hasCoverPreview: !!document.querySelector('.js_cover_preview_new') && getComputedStyle(document.querySelector('.js_cover_preview_new')).backgroundImage !== 'none',
    coverFlow: $($coverFlowResult | ConvertTo-Json -Compress)
  }, null, 2);
})()
"@
Invoke-AgentBrowserEval -Script $verifyScript
