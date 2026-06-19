param(
    [string]$WechatDir,
    [string]$XhsDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Drawing

function Get-FontFamily {
    param([string[]]$Candidates)
    foreach ($name in $Candidates) {
        try {
            $font = New-Object System.Drawing.Font($name, 12)
            if ($font.Name -eq $name) {
                return $name
            }
        } catch {
        }
    }
    return 'Arial'
}

function New-Brush {
    param([string]$Hex)
    return New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml($Hex))
}

function New-Pen {
    param([string]$Hex, [float]$Width = 1)
    return New-Object System.Drawing.Pen([System.Drawing.ColorTranslator]::FromHtml($Hex), $Width)
}

function Draw-WrappedText {
    param(
        [System.Drawing.Graphics]$Graphics,
        [string]$Text,
        [System.Drawing.Font]$Font,
        [System.Drawing.Brush]$Brush,
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$LineHeight,
        [int]$MaxLines = 100
    )

    $lines = @()
    foreach ($paragraph in ($Text -split "`n")) {
        if ([string]::IsNullOrWhiteSpace($paragraph)) {
            $lines += ''
            continue
        }

        $current = ''
        foreach ($char in $paragraph.ToCharArray()) {
            $candidate = $current + $char
            $size = $Graphics.MeasureString($candidate, $Font)
            if ($size.Width -gt $Width -and $current.Length -gt 0) {
                $lines += $current
                $current = [string]$char
            } else {
                $current = $candidate
            }
        }

        if ($current.Length -gt 0) {
            $lines += $current
        }
    }

    $drawn = 0
    foreach ($line in $lines) {
        if ($drawn -ge $MaxLines) {
            break
        }
        $Graphics.DrawString($line, $Font, $Brush, $X, $Y + ($drawn * $LineHeight))
        $drawn += 1
    }
}

function Save-Png {
    param(
        [System.Drawing.Bitmap]$Bitmap,
        [string]$Path
    )
    $dir = Split-Path -Parent $Path
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force $dir | Out-Null
    }
    $Bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
}

function Draw-BaseBackground {
    param(
        [System.Drawing.Graphics]$Graphics,
        [int]$Width,
        [int]$Height,
        [string]$BackgroundPath
    )

    $Graphics.Clear([System.Drawing.ColorTranslator]::FromHtml('#F7F1E8'))
    if ($BackgroundPath -and (Test-Path $BackgroundPath)) {
        $bg = [System.Drawing.Image]::FromFile($BackgroundPath)
        try {
            $Graphics.DrawImage($bg, 0, 0, $Width, $Height)
        } finally {
            $bg.Dispose()
        }
    }

    $overlay = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(188, 247, 241, 232))
    $Graphics.FillRectangle($overlay, 0, 0, $Width, $Height)
    $overlay.Dispose()
}

function Draw-AccentBlocks {
    param(
        [System.Drawing.Graphics]$Graphics,
        [int]$Width,
        [int]$Height
    )

    $orange = New-Brush -Hex '#F29F58'
    $green = New-Brush -Hex '#2E5E4E'
    $light = New-Brush -Hex '#FFF8F0'
    $Graphics.FillEllipse($orange, $Width - 270, 60, 170, 170)
    $Graphics.FillRectangle($green, 70, $Height - 180, 150, 18)
    $Graphics.FillRectangle($orange, 70, $Height - 145, 220, 12)
    $Graphics.FillRectangle($light, 0, 0, $Width, $Height)
    $orange.Dispose()
    $green.Dispose()
    $light.Dispose()
}

function New-WechatCover {
    param(
        [string]$OutputPath,
        [string]$BackgroundPath,
        [string]$Title,
        [string]$Subtitle
    )

    $bmp = New-Object System.Drawing.Bitmap 900, 383
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    try {
        $g.SmoothingMode = 'HighQuality'
        $g.TextRenderingHint = 'AntiAliasGridFit'
        Draw-BaseBackground -Graphics $g -Width 900 -Height 383 -BackgroundPath $BackgroundPath

        $panel = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(210, 255, 250, 242))
        $g.FillRectangle($panel, 40, 40, 510, 300)

        $family = Get-FontFamily @('Microsoft YaHei UI', 'Microsoft YaHei', 'Segoe UI')
        $titleFont = New-Object System.Drawing.Font($family, 34, [System.Drawing.FontStyle]::Bold)
        $subFont = New-Object System.Drawing.Font($family, 16, [System.Drawing.FontStyle]::Regular)
        $brandFont = New-Object System.Drawing.Font($family, 14, [System.Drawing.FontStyle]::Bold)
        $dark = New-Brush -Hex '#20342E'
        $accent = New-Brush -Hex '#D97A2B'

        $g.DrawString('AI趣创社', $brandFont, $accent, 68, 74)
        Draw-WrappedText -Graphics $g -Text $Title -Font $titleFont -Brush $dark -X 68 -Y 118 -Width 450 -LineHeight 44 -MaxLines 3
        Draw-WrappedText -Graphics $g -Text $Subtitle -Font $subFont -Brush $dark -X 70 -Y 258 -Width 420 -LineHeight 24 -MaxLines 3

        $linePen = New-Pen -Hex '#F29F58' -Width 6
        $g.DrawLine($linePen, 610, 70, 610, 308)
        $g.DrawLine($linePen, 640, 70, 640, 250)

        $panel.Dispose()
        $titleFont.Dispose()
        $subFont.Dispose()
        $brandFont.Dispose()
        $dark.Dispose()
        $accent.Dispose()
        $linePen.Dispose()
        Save-Png -Bitmap $bmp -Path $OutputPath
    } finally {
        $g.Dispose()
        $bmp.Dispose()
    }
}

function New-WechatDiagram {
    param(
        [string]$OutputPath,
        [string]$Title,
        [string[]]$Items,
        [string]$Footer = ''
    )

    $bmp = New-Object System.Drawing.Bitmap 1200, 900
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    try {
        $g.SmoothingMode = 'HighQuality'
        $g.TextRenderingHint = 'AntiAliasGridFit'
        $g.Clear([System.Drawing.ColorTranslator]::FromHtml('#FBF6EF'))

        $family = Get-FontFamily @('Microsoft YaHei UI', 'Microsoft YaHei', 'Segoe UI')
        $titleFont = New-Object System.Drawing.Font($family, 30, [System.Drawing.FontStyle]::Bold)
        $itemFont = New-Object System.Drawing.Font($family, 20, [System.Drawing.FontStyle]::Regular)
        $footerFont = New-Object System.Drawing.Font($family, 16, [System.Drawing.FontStyle]::Regular)
        $dark = New-Brush -Hex '#20342E'
        $orange = New-Brush -Hex '#F29F58'
        $green = New-Brush -Hex '#2E5E4E'
        $white = New-Brush -Hex '#FFFDF9'
        $pen = New-Pen -Hex '#E8D7C4' -Width 2

        $g.DrawString($Title, $titleFont, $dark, 80, 70)

        $top = 180
        foreach ($item in $Items) {
            $g.FillRoundedRectangle($white, 90, $top, 1020, 92, 18)
            $g.DrawRoundedRectangle($pen, 90, $top, 1020, 92, 18)
            $g.FillEllipse($orange, 120, $top + 24, 42, 42)
            $g.DrawString($item, $itemFont, $green, 190, $top + 28)
            $top += 110
        }

        if ($Footer) {
            $g.DrawString($Footer, $footerFont, $dark, 92, 820)
        }

        $titleFont.Dispose()
        $itemFont.Dispose()
        $footerFont.Dispose()
        $dark.Dispose()
        $orange.Dispose()
        $green.Dispose()
        $white.Dispose()
        $pen.Dispose()
        Save-Png -Bitmap $bmp -Path $OutputPath
    } finally {
        $g.Dispose()
        $bmp.Dispose()
    }
}

Update-TypeData -TypeName System.Drawing.Graphics -MemberName FillRoundedRectangle -MemberType ScriptMethod -Value {
    param($Brush, $X, $Y, $Width, $Height, $Radius)
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $path.AddArc($X, $Y, $Radius, $Radius, 180, 90)
    $path.AddArc($X + $Width - $Radius, $Y, $Radius, $Radius, 270, 90)
    $path.AddArc($X + $Width - $Radius, $Y + $Height - $Radius, $Radius, $Radius, 0, 90)
    $path.AddArc($X, $Y + $Height - $Radius, $Radius, $Radius, 90, 90)
    $path.CloseFigure()
    $this.FillPath($Brush, $path)
    $path.Dispose()
}

Update-TypeData -TypeName System.Drawing.Graphics -MemberName DrawRoundedRectangle -MemberType ScriptMethod -Value {
    param($Pen, $X, $Y, $Width, $Height, $Radius)
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $path.AddArc($X, $Y, $Radius, $Radius, 180, 90)
    $path.AddArc($X + $Width - $Radius, $Y, $Radius, $Radius, 270, 90)
    $path.AddArc($X + $Width - $Radius, $Y + $Height - $Radius, $Radius, $Radius, 0, 90)
    $path.AddArc($X, $Y + $Height - $Radius, $Radius, $Radius, 90, 90)
    $path.CloseFigure()
    $this.DrawPath($Pen, $path)
    $path.Dispose()
}

function New-XhsCard {
    param(
        [string]$OutputPath,
        [string]$Title,
        [string[]]$BodyLines,
        [string]$TagLine = '',
        [string]$BackgroundPath = ''
    )

    $bmp = New-Object System.Drawing.Bitmap 1242, 1660
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    try {
        $g.SmoothingMode = 'HighQuality'
        $g.TextRenderingHint = 'AntiAliasGridFit'
        Draw-BaseBackground -Graphics $g -Width 1242 -Height 1660 -BackgroundPath $BackgroundPath

        $topBlock = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(220, 255, 250, 242))
        $bodyBlock = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(230, 255, 253, 249))
        $g.FillRoundedRectangle($topBlock, 70, 70, 1102, 340, 32)
        $g.FillRoundedRectangle($bodyBlock, 70, 455, 1102, 1030, 32)

        $family = Get-FontFamily @('Microsoft YaHei UI', 'Microsoft YaHei', 'Segoe UI')
        $titleFont = New-Object System.Drawing.Font($family, 48, [System.Drawing.FontStyle]::Bold)
        $bodyFont = New-Object System.Drawing.Font($family, 30, [System.Drawing.FontStyle]::Regular)
        $tagFont = New-Object System.Drawing.Font($family, 22, [System.Drawing.FontStyle]::Bold)
        $brandFont = New-Object System.Drawing.Font($family, 22, [System.Drawing.FontStyle]::Bold)
        $dark = New-Brush -Hex '#20342E'
        $green = New-Brush -Hex '#2E5E4E'
        $orange = New-Brush -Hex '#F29F58'

        $g.DrawString('AI趣创社', $brandFont, $orange, 120, 112)
        Draw-WrappedText -Graphics $g -Text $Title -Font $titleFont -Brush $dark -X 118 -Y 170 -Width 900 -LineHeight 58 -MaxLines 4

        $y = 540
        foreach ($line in $BodyLines) {
            if ([string]::IsNullOrWhiteSpace($line)) {
                $y += 28
                continue
            }
            if ($line.StartsWith('- ')) {
                $g.FillEllipse($orange, 125, $y + 12, 14, 14)
                Draw-WrappedText -Graphics $g -Text $line.Substring(2) -Font $bodyFont -Brush $green -X 160 -Y $y -Width 900 -LineHeight 42 -MaxLines 3
                $y += 88
            } else {
                Draw-WrappedText -Graphics $g -Text $line -Font $bodyFont -Brush $green -X 120 -Y $y -Width 960 -LineHeight 42 -MaxLines 4
                $y += 86
            }
        }

        if ($TagLine) {
            $tagBlock = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 242, 159, 88))
            $g.FillRoundedRectangle($tagBlock, 100, 1520, 500, 70, 20)
            $tagTextBrush = New-Brush -Hex '#FFFDF9'
            $g.DrawString($TagLine, $tagFont, $tagTextBrush, 126, 1538)
            $tagTextBrush.Dispose()
            $tagBlock.Dispose()
        }

        $topBlock.Dispose()
        $bodyBlock.Dispose()
        $titleFont.Dispose()
        $bodyFont.Dispose()
        $tagFont.Dispose()
        $brandFont.Dispose()
        $dark.Dispose()
        $green.Dispose()
        $orange.Dispose()
        Save-Png -Bitmap $bmp -Path $OutputPath
    } finally {
        $g.Dispose()
        $bmp.Dispose()
    }
}

$wechatBase = Join-Path $WechatDir 'images\wechat_cover_base.png'
$xhsBase = Join-Path $XhsDir 'images\xhs_cover_base.png'

New-WechatCover `
    -OutputPath (Join-Path $WechatDir 'images\01_公众号封面.png') `
    -BackgroundPath $wechatBase `
    -Title '一套适合普通创作者的AI内容生产SOP' `
    -Subtitle '从选题到发布，怎么真正跑顺'

New-WechatDiagram `
    -OutputPath (Join-Path $WechatDir 'images\02_为什么用了AI还是没提效.png') `
    -Title '为什么很多人用了 AI 还是没提效' `
    -Items @(
        '今天写标题，明天换工具，后天又重写一遍',
        '看起来一直很忙，其实没有固定流程',
        '真正缺的不是工具，而是能反复跑起来的 SOP'
    ) `
    -Footer '先固定步骤，再让 AI 进入步骤里承担角色。'

New-WechatDiagram `
    -OutputPath (Join-Path $WechatDir 'images\03_六步SOP总览.png') `
    -Title '基础版内容生产 SOP：6 步跑顺' `
    -Items @(
        '1. 拆受众问题',
        '2. 扩选题角度',
        '3. 搭文章提纲',
        '4. 写初稿并补表达',
        '5. 改成平台版本',
        '6. 补承接动作后发布'
    ) `
    -Footer '先把顺序固定，再逐步模板化。'

New-WechatDiagram `
    -OutputPath (Join-Path $WechatDir 'images\04_AI和人分别负责什么.png') `
    -Title 'AI 和人，分别该负责什么' `
    -Items @(
        'AI 负责：整理、扩展、提速、改写',
        '你负责：方向、取舍、观点、结论',
        '判断不外包，内容才不会越来越像机器'
    ) `
    -Footer 'AI 是提速器，不是判断替代者。'

$xhsCards = @(
    @{
        File = '01_首图.png'
        Title = '内容创作者最该先学的 1 条 AI 图文流程'
        Body = @(
            '不是多学工具。',
            '而是先让自己有一条能反复跑起来的流程。',
            '',
            '- 先跑顺，再提速',
            '- 先稳定，再升级'
        )
        Tag = '先搭流程'
        Background = $xhsBase
    },
    @{
        File = '02_问题页.png'
        Title = '为什么你学了 AI 还是不稳定'
        Body = @(
            '不是你不努力。',
            '而是你每天都在临场发挥。',
            '',
            '- 想选题靠现想',
            '- 写结构靠感觉',
            '- 改平台版本靠重写'
        )
        Tag = '问题先看清'
        Background = ''
    },
    @{
        File = '03_流程总览.png'
        Title = '这条基础流程怎么跑'
        Body = @(
            '- 拆痛点',
            '- 扩选题',
            '- 搭提纲',
            '- 写初稿',
            '- 改平台版',
            '- 发前检查'
        )
        Tag = '6步跑顺'
        Background = ''
    },
    @{
        File = '04_前三步.png'
        Title = '先把前 3 步跑顺'
        Body = @(
            '1. 先拆受众痛点',
            '2. 再铺 5 到 10 个选题角度',
            '3. 先搭提纲，不要直接写全文'
        )
        Tag = '前3步'
        Background = ''
    },
    @{
        File = '05_后三步.png'
        Title = '后 3 步决定你像不像自己'
        Body = @(
            '4. 初稿出来后，自己补判断',
            '5. 再让 AI 改成平台版本',
            '6. 发前一定补上承接动作'
        )
        Tag = '后3步'
        Background = ''
    },
    @{
        File = '06_关键提醒.png'
        Title = '最关键的不是 AI 帮你写完'
        Body = @(
            '- AI 负责提速',
            '- 你负责方向',
            '- 你负责最终判断',
            '',
            '这样内容才不会越来越像机器。'
        )
        Tag = '别把判断交出去'
        Background = ''
    },
    @{
        File = '07_CTA页.png'
        Title = '先把这条流程跑顺'
        Body = @(
            '产出会更稳。',
            '脑子会没那么乱。',
            '内容也会更像你自己。',
            '',
            '想看基础版清单，私信我 `流程`。'
        )
        Tag = '私信我 流程'
        Background = ''
    }
)

foreach ($card in $xhsCards) {
    New-XhsCard `
        -OutputPath (Join-Path $XhsDir ('images\' + $card.File)) `
        -Title $card.Title `
        -BodyLines $card.Body `
        -TagLine $card.Tag `
        -BackgroundPath $card.Background
}
