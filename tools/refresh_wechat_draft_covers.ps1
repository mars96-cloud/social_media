[CmdletBinding()]
param(
    [string]$Session = "wechat-batch",
    [string]$Token = "1740056467",
    [int]$MaxItems = 0
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root = Split-Path -Parent $PSScriptRoot
$opsRoot = Get-ChildItem -LiteralPath $root -Directory | Where-Object { $_.Name -like "06_*" } | Select-Object -First 1
if (-not $opsRoot) {
    throw "Cannot locate operations root under workspace."
}
$yearRoot = Join-Path $opsRoot.FullName "2026"
$tmpRoot = "C:\tmp\wechat-cover-refresh"
$draftListUrl = "https://mp.weixin.qq.com/cgi-bin/appmsg?begin=0&count=10&type=77&action=list_card&token=$Token&lang=zh_CN"

$articles = @()
foreach ($month in @("2026-06", "2026-07")) {
    $monthRoot = Join-Path $yearRoot $month
    $draftDir = Get-ChildItem -LiteralPath $monthRoot -Directory | Where-Object { $_.Name -like "*稿区" } | Select-Object -First 1
    if (-not $draftDir) {
        continue
    }
    $monthDraftRoot = $draftDir.FullName
    if (-not (Test-Path -LiteralPath $monthDraftRoot)) {
        continue
    }

    Get-ChildItem -LiteralPath $monthDraftRoot -Directory | ForEach-Object {
        $metadataPath = Join-Path $_.FullName "metadata.json"
        $coverPath = Join-Path $_.FullName "images\01_公众号封面.png"
        if (-not (Test-Path -LiteralPath $metadataPath) -or -not (Test-Path -LiteralPath $coverPath)) {
            return
        }

        $metadata = Get-Content -Raw -Encoding UTF8 -LiteralPath $metadataPath | ConvertFrom-Json
        $articles += [pscustomobject]@{
            Title = [string]$metadata.title
            Cover = $coverPath
        }
    }
}

function Invoke-AgentBrowser {
    param([string[]]$Args)
    & npx.cmd --yes agent-browser --session $Session @Args
    if ($LASTEXITCODE -ne 0) {
        throw "agent-browser failed: $($Args -join ' ')"
    }
}

function Invoke-AgentBrowserEval {
    param([string]$Script)
    $tmp = Join-Path $env:TEMP ("codex-wechat-refresh-" + [guid]::NewGuid().ToString() + ".js")
    Set-Content -LiteralPath $tmp -Value $Script -Encoding UTF8
    try {
        Get-Content -Raw -Encoding UTF8 -LiteralPath $tmp | & npx.cmd --yes agent-browser --session $Session eval --stdin
        if ($LASTEXITCODE -ne 0) {
            throw "agent-browser eval failed"
        }
    }
    finally {
        Remove-Item -LiteralPath $tmp -ErrorAction SilentlyContinue
    }
}

function Wait-Millis([int]$Ms) {
    Invoke-AgentBrowser @("wait", "$Ms")
}

function Open-DraftList {
    Invoke-AgentBrowser @("open", $draftListUrl)
    Invoke-AgentBrowser @("wait", "--load", "networkidle")
    Wait-Millis 1200
}

function Search-Draft([string]$Title) {
    $escaped = $Title.Replace("\", "\\").Replace("'", "\'")
    $script = @'
(() => {
  const input = document.querySelector('input[type="text"]');
  if (!input) throw new Error('search input not found');
  input.focus();
  input.value = '__TITLE__';
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  const btn = Array.from(document.querySelectorAll('button')).find(el => {
    const text = (el.innerText || '').trim();
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0 && !text;
  });
  if (btn) btn.click();
  return 'searched';
})()
'@
    $script = $script.Replace('__TITLE__', $escaped)
    Invoke-AgentBrowserEval -Script $script | Out-Null
    Wait-Millis 1500
}

function Open-DraftEditor([string]$Title) {
    $escaped = $Title.Replace("\", "\\").Replace("'", "\'")
    $script = @'
(() => {
  const match = Array.from(document.querySelectorAll('a'))
    .find(el => (el.innerText || '').trim() === '__TITLE__');
  if (!match) return 'NOT_FOUND';
  match.click();
  return 'OPENED';
})()
'@
    $script = $script.Replace('__TITLE__', $escaped)
    $result = Invoke-AgentBrowserEval -Script $script
    if ($result -match "NOT_FOUND") {
        return $false
    }
    Invoke-AgentBrowser @("wait", "--load", "networkidle")
    Wait-Millis 1800
    return $true
}

function Upload-CoverAsset([string]$SourcePath, [string]$UniqueName) {
    $targetDir = New-Item -ItemType Directory -Force -Path $tmpRoot
    $targetPath = Join-Path $targetDir.FullName $UniqueName
    Copy-Item -LiteralPath $SourcePath -Destination $targetPath -Force
    Invoke-AgentBrowser @("upload", "input[type=file]", $targetPath)
    Wait-Millis 1800
    return $targetPath
}

function Open-CoverDialog {
    $script = @'
(() => {
  const btn = document.querySelector('#js_cover_description_area .js_imagedialog');
  if (!btn) throw new Error('cover image library button not found');
  btn.click();
  return 'opened';
})()
'@
    Invoke-AgentBrowserEval -Script $script | Out-Null
    Wait-Millis 1500
}

function Select-CoverItem([string]$FileName) {
    $escaped = $FileName.Replace("\", "\\").Replace("'", "\'")
    $script = @'
(() => {
  const candidates = Array.from(document.querySelectorAll('*'))
    .map(el => ({
      el,
      txt: (el.innerText || '').trim(),
      rect: el.getBoundingClientRect()
    }))
    .filter(x => x.txt === '__FILE__' && x.rect.width > 0 && x.rect.height > 0)
    .sort((a, b) => a.rect.top - b.rect.top);
  const target = candidates[0]?.el;
  if (!target) throw new Error('uploaded cover item not found');
  target.click();
  return target.innerText;
})()
'@
    $script = $script.Replace('__FILE__', $escaped)
    Invoke-AgentBrowserEval -Script $script | Out-Null
    Wait-Millis 1000
}

function Complete-CoverDialogFlow {
    $stateScript = @'
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
  const visibleActions = Array.from(document.querySelectorAll('button, a, [role="button"], .weui-desktop-btn'))
    .map(el => ({ el, text: (el.innerText || '').trim(), rect: el.getBoundingClientRect() }))
    .filter(x => x.rect.width > 0 && x.rect.height > 0);
  const isSave = text => text.includes(saveDraftText) || text === saveText;
  const dialogButton = visibleActions
    .filter(x => x.text && !isSave(x.text))
    .sort((a, b) => (b.rect.top - a.rect.top) || (b.rect.left - a.rect.left))[0];
  const saveButton = visibleActions.find(x => isSave(x.text));
  if (title.includes(chooseTitle) || title.includes(editTitle)) {
    if (!dialogButton) throw new Error('dialog button not found');
    dialogButton.el.click();
    return JSON.stringify({ step: title, button: dialogButton.text });
  }
  if (saveButton) {
    saveButton.el.click();
    return JSON.stringify({ step: 'save', button: saveButton.text });
  }
  return JSON.stringify({ step: 'idle', title });
})()
'@
    1..3 | ForEach-Object {
        Invoke-AgentBrowserEval -Script $stateScript | Out-Null
        Wait-Millis 1800
    }
}

function Save-DraftIfNeeded {
    $script = @'
(() => {
  const actions = Array.from(document.querySelectorAll('button, a, [role="button"], .weui-desktop-btn'))
    .map(el => ({ el, text: (el.innerText || '').trim(), rect: el.getBoundingClientRect() }))
    .filter(x => x.text && x.rect.width > 0 && x.rect.height > 0);
  const save = actions.find(x => x.text.includes('\u4fdd\u5b58\u4e3a\u8349\u7a3f') || x.text === '\u4fdd\u5b58');
  if (!save) return 'NO_SAVE_BUTTON';
  save.el.click();
  return save.text;
})()
'@
    Invoke-AgentBrowserEval -Script $script | Out-Null
    Wait-Millis 2500
}

function Verify-CoverApplied([string]$Title) {
    $escaped = $Title.Replace("\", "\\").Replace("'", "\'")
    $script = @'
(() => {
  const pageTitle = document.querySelectorAll('.ProseMirror')[0]?.innerText || '';
  const coverPreview = getComputedStyle(document.querySelector('.js_cover_preview_new')).backgroundImage;
  return JSON.stringify({
    titleOk: pageTitle.includes('__TITLE__'),
    hasCoverPreview: !!document.querySelector('.js_cover_preview_new') && coverPreview !== 'none',
    preview: coverPreview
  });
})()
'@
    $script = $script.Replace('__TITLE__', $escaped)
    return Invoke-AgentBrowserEval -Script $script
}

$results = @()

if ($MaxItems -gt 0) {
    $articles = $articles | Select-Object -First $MaxItems
}

foreach ($item in $articles) {
    if (-not (Test-Path -LiteralPath $item.Cover)) {
        $results += [pscustomobject]@{ title = $item.Title; status = "cover-missing"; cover = $item.Cover }
        continue
    }

    Open-DraftList
    Search-Draft -Title $item.Title
    if (-not (Open-DraftEditor -Title $item.Title)) {
        $results += [pscustomobject]@{ title = $item.Title; status = "draft-not-found"; cover = $item.Cover }
        continue
    }

    $slug = [System.Text.RegularExpressions.Regex]::Replace($item.Title, '[^\p{L}\p{Nd}]', '')
    if (-not $slug) {
        $slug = [guid]::NewGuid().ToString("N")
    }
    $uniqueName = "$slug-cover.png"
    Upload-CoverAsset -SourcePath $item.Cover -UniqueName $uniqueName | Out-Null
    Open-CoverDialog
    Select-CoverItem -FileName $uniqueName
    Complete-CoverDialogFlow
    Save-DraftIfNeeded
    $verify = Verify-CoverApplied -Title $item.Title

    $results += [pscustomobject]@{
        title = $item.Title
        status = "saved"
        uploaded = $uniqueName
        verify = $verify
    }
}

$results | ConvertTo-Json -Depth 6
