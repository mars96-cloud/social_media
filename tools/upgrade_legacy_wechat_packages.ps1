[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Root
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.Drawing

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Write-Utf8File {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Content
    )
    [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
}

function New-CanvasImage {
    param(
        [Parameter(Mandatory = $true)][string]$SourcePath,
        [Parameter(Mandatory = $true)][string]$OutPath,
        [Parameter(Mandatory = $true)][int]$Width,
        [Parameter(Mandatory = $true)][int]$Height
    )

    $src = [System.Drawing.Bitmap]::new($SourcePath)
    try {
        $dst = [System.Drawing.Bitmap]::new($Width, $Height)
        try {
            $bg = $src.GetPixel([Math]::Min(15, $src.Width - 1), [Math]::Min(15, $src.Height - 1))
            $g = [System.Drawing.Graphics]::FromImage($dst)
            try {
                $g.Clear($bg)
                $g.SmoothingMode = 'HighQuality'
                $g.InterpolationMode = 'HighQualityBicubic'
                $g.PixelOffsetMode = 'HighQuality'
                $ratio = [Math]::Min($Width / $src.Width, $Height / $src.Height)
                $drawW = [int][Math]::Round($src.Width * $ratio)
                $drawH = [int][Math]::Round($src.Height * $ratio)
                $drawX = [int][Math]::Round(($Width - $drawW) / 2)
                $drawY = [int][Math]::Round(($Height - $drawH) / 2)
                $g.DrawImage($src, [System.Drawing.Rectangle]::new($drawX, $drawY, $drawW, $drawH))
            } finally {
                $g.Dispose()
            }
            $dst.Save($OutPath, [System.Drawing.Imaging.ImageFormat]::Png)
        } finally {
            $dst.Dispose()
        }
    } finally {
        $src.Dispose()
    }
}

function Get-Digest {
    param([string[]]$Lines)
    $parts = @()
    foreach ($line in $Lines) {
        $text = $line.Trim()
        if (-not $text) { continue }
        if ($text -match '^【配图：') { continue }
        if ($text -match '^[一二三四五六七八九十]+、') { break }
        $parts += $text
        if (($parts -join '') .Length -ge 90) { break }
    }
    $digest = ($parts -join '')
    if ($digest.Length -gt 110) {
        $digest = $digest.Substring(0, 110)
    }
    return $digest
}

function Build-Mapping {
    param(
        [string]$Title,
        [string[]]$Lines
    )

    $majorHeadings = New-Object System.Collections.Generic.List[string]
    $records = New-Object System.Collections.Generic.List[object]
    $currentMajor = ""
    $currentParagraph = 0

    foreach ($raw in $Lines) {
        $line = $raw.Trim()
        if (-not $line) { continue }
        if ($line -eq $Title) { continue }
        if ($line -match '^[一二三四五六七八九十]+、') {
            $currentMajor = $line
            $majorHeadings.Add($line)
            $currentParagraph = 0
            continue
        }
        if ($line -match '^【配图：(.+?)】$') {
            $file = $Matches[1]
            $records.Add([PSCustomObject]@{
                File = $file
                Heading = $currentMajor
                Paragraph = [Math]::Max($currentParagraph, 1)
            })
            continue
        }
        $currentParagraph += 1
    }

    $sb = New-Object System.Text.StringBuilder
    [void]$sb.AppendLine('# 正文结构与配图映射')
    [void]$sb.AppendLine()
    [void]$sb.AppendLine('## 文章层级')
    [void]$sb.AppendLine()
    [void]$sb.AppendLine("- 一级标题：$Title")
    $index = 1
    foreach ($heading in $majorHeadings) {
        [void]$sb.AppendLine("- 二级标题 $index：$heading")
        $index += 1
    }
    [void]$sb.AppendLine()
    [void]$sb.AppendLine('## 配图映射')
    [void]$sb.AppendLine()
    [void]$sb.AppendLine('### 图 01 封面')
    [void]$sb.AppendLine()
    [void]$sb.AppendLine('- 文件：images/01_公众号封面_标题版_2.35比1.png')
    [void]$sb.AppendLine('- 用途：封面')
    [void]$sb.AppendLine('- 不进入正文')
    [void]$sb.AppendLine()

    $imgIndex = 2
    foreach ($record in $records) {
        [void]$sb.AppendLine("### 图 $imgIndex 正文图")
        [void]$sb.AppendLine()
        [void]$sb.AppendLine("- 文件：images/$($record.File)")
        [void]$sb.AppendLine("- 插在：$($record.Heading) 下，第 $($record.Paragraph) 段后")
        [void]$sb.AppendLine('- 作用：承接该节核心判断')
        [void]$sb.AppendLine()
        $imgIndex += 1
    }

    return $sb.ToString().TrimEnd() + "`r`n"
}

$rootPath = (Resolve-Path -LiteralPath $Root).Path
$packages = Get-ChildItem -LiteralPath $rootPath -Directory | Where-Object { $_.Name -ne '_样张对比' }
$results = @()

foreach ($pkg in $packages) {
    $pkgPath = $pkg.FullName
    $imagesDir = Join-Path $pkgPath 'images'
    $bodyPath = Join-Path $pkgPath '草稿箱正文.txt'
    $metaPath = Join-Path $pkgPath 'metadata.json'
    $coverOld = Join-Path $imagesDir '01_公众号封面.png'
    if (-not ((Test-Path $imagesDir) -and (Test-Path $bodyPath) -and (Test-Path $metaPath) -and (Test-Path $coverOld))) {
        continue
    }

    $bodyLines = [System.IO.File]::ReadAllLines($bodyPath, $utf8NoBom)
    $cleanLines = New-Object System.Collections.Generic.List[string]
    $removedFirstCover = $false
    foreach ($line in $bodyLines) {
        if (-not $removedFirstCover -and $line.Trim() -match '^【配图：01_公众号封面(\.png)?】$') {
            $removedFirstCover = $true
            continue
        }
        $cleanLines.Add($line)
    }
    if ($removedFirstCover) {
        Write-Utf8File -Path $bodyPath -Content (($cleanLines -join "`r`n").TrimEnd() + "`r`n")
    }

    $title = ""
    foreach ($line in $cleanLines) {
        if ($line.Trim()) { $title = $line.Trim(); break }
    }
    if (-not $title) { continue }

    $wideTitle = Join-Path $imagesDir '01_公众号封面_标题版_2.35比1.png'
    $squareTitle = Join-Path $imagesDir '01_公众号封面_标题版_1比1.png'
    $wideBase = Join-Path $imagesDir '01_公众号封面_底图_2.35比1.png'
    $squareBase = Join-Path $imagesDir '01_公众号封面_底图_1比1.png'
    New-CanvasImage -SourcePath $coverOld -OutPath $wideTitle -Width 2820 -Height 1200
    New-CanvasImage -SourcePath $coverOld -OutPath $squareTitle -Width 1600 -Height 1600
    Copy-Item -LiteralPath $wideTitle -Destination $wideBase -Force
    Copy-Item -LiteralPath $squareTitle -Destination $squareBase -Force

    $legacyMeta = Get-Content -LiteralPath $metaPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $bodyImagePaths = @()
    foreach ($file in ($legacyMeta.image_files | Where-Object { $_ -and ($_ -notlike '01_公众号封面*') })) {
        $bodyImagePaths += ("images/" + $file)
    }
    $digest = Get-Digest -Lines ($cleanLines | Select-Object -Skip 1)
    $newMeta = [ordered]@{
        platform = 'wechat'
        title = $title
        digest = $digest
        source_article = ''
        cover_path = 'images/01_公众号封面_标题版_2.35比1.png'
        body_image_paths = $bodyImagePaths
        status = 'draft-ready'
        legacy = $legacyMeta
    }
    Write-Utf8File -Path $metaPath -Content (($newMeta | ConvertTo-Json -Depth 6))

    $mappingPath = Join-Path $pkgPath '正文结构与配图映射.md'
    $mapping = Build-Mapping -Title $title -Lines $cleanLines
    Write-Utf8File -Path $mappingPath -Content $mapping

    $results += [PSCustomObject]@{
        Package = $pkg.Name
        Title = $title
        Cover = 'images/01_公众号封面_标题版_2.35比1.png'
        BodyImageCount = $bodyImagePaths.Count
        RemovedBodyCover = $removedFirstCover
    }
}

$results | ConvertTo-Json -Depth 4
