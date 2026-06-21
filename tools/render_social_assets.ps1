param(
    [Parameter(Mandatory = $true)]
    [string]$WechatDir,
    [Parameter(Mandatory = $true)]
    [string]$XhsDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

function Get-Color {
    param([string]$Hex)
    return [System.Drawing.ColorTranslator]::FromHtml($Hex)
}

function New-Brush {
    param([string]$Hex)
    return New-Object -TypeName System.Drawing.SolidBrush -ArgumentList $(Get-Color $Hex)
}

function New-Pen {
    param([string]$Hex, [float]$Width = 1)
    return New-Object -TypeName System.Drawing.Pen -ArgumentList $(Get-Color $Hex), $Width
}

function Get-FontFamily {
    param([string[]]$Candidates)
    foreach ($name in $Candidates) {
        try {
            $font = New-Object -TypeName System.Drawing.Font -ArgumentList $name, 12
            if ($font.Name -eq $name) {
                $font.Dispose()
                return $name
            }
            $font.Dispose()
        } catch {
        }
    }
    return 'Arial'
}

function New-Font {
    param(
        [float]$Size,
        [bool]$Bold = $false
    )
    $family = Get-FontFamily @('Microsoft YaHei UI', 'Microsoft YaHei', 'Segoe UI', 'Arial')
    $style = if ($Bold) { [System.Drawing.FontStyle]::Bold } else { [System.Drawing.FontStyle]::Regular }
    return New-Object -TypeName System.Drawing.Font -ArgumentList $family, $Size, $style
}

function New-RoundedPath {
    param(
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$Height,
        [float]$Radius
    )
    $path = New-Object -TypeName System.Drawing.Drawing2D.GraphicsPath
    $diameter = $Radius * 2
    $path.AddArc($X, $Y, $diameter, $diameter, 180, 90)
    $path.AddArc($X + $Width - $diameter, $Y, $diameter, $diameter, 270, 90)
    $path.AddArc($X + $Width - $diameter, $Y + $Height - $diameter, $diameter, $diameter, 0, 90)
    $path.AddArc($X, $Y + $Height - $diameter, $diameter, $diameter, 90, 90)
    $path.CloseFigure()
    return $path
}

function Fill-RoundedRectangle {
    param(
        [System.Drawing.Graphics]$Graphics,
        [System.Drawing.Brush]$Brush,
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$Height,
        [float]$Radius
    )
    $path = New-RoundedPath -X $X -Y $Y -Width $Width -Height $Height -Radius $Radius
    try {
        $Graphics.FillPath($Brush, $path)
    } finally {
        $path.Dispose()
    }
}

function Draw-RoundedRectangle {
    param(
        [System.Drawing.Graphics]$Graphics,
        [System.Drawing.Pen]$Pen,
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$Height,
        [float]$Radius
    )
    $path = New-RoundedPath -X $X -Y $Y -Width $Width -Height $Height -Radius $Radius
    try {
        $Graphics.DrawPath($Pen, $path)
    } finally {
        $path.Dispose()
    }
}

function Get-TextWidth {
    param(
        [System.Drawing.Graphics]$Graphics,
        [string]$Text,
        [System.Drawing.Font]$Font
    )
    $size = $Graphics.MeasureString($Text, $Font)
    return [int][Math]::Ceiling($size.Width)
}

function Get-WrappedLines {
    param(
        [System.Drawing.Graphics]$Graphics,
        [string]$Text,
        [System.Drawing.Font]$Font,
        [float]$MaxWidth
    )
    $lines = New-Object System.Collections.Generic.List[string]
    foreach ($paragraph in ($Text -split "`n")) {
        if ([string]::IsNullOrWhiteSpace($paragraph)) {
            [void]$lines.Add('')
            continue
        }
        $current = ''
        foreach ($char in $paragraph.ToCharArray()) {
            $candidate = $current + $char
            if ($current.Length -gt 0 -and (Get-TextWidth -Graphics $Graphics -Text $candidate -Font $Font) -gt $MaxWidth) {
                [void]$lines.Add($current)
                $current = [string]$char
            } else {
                $current = $candidate
            }
        }
        if ($current.Length -gt 0) {
            [void]$lines.Add($current)
        }
    }
    return ,$lines.ToArray()
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
    $lines = Get-WrappedLines -Graphics $Graphics -Text $Text -Font $Font -MaxWidth $Width
    $count = [Math]::Min($lines.Count, $MaxLines)
    for ($i = 0; $i -lt $count; $i++) {
        $Graphics.DrawString($lines[$i], $Font, $Brush, $X, $Y + ($i * $LineHeight))
    }
    return $Y + ($count * $LineHeight)
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

function New-Canvas {
    param(
        [int]$Width,
        [int]$Height
    )
    $bmp = New-Object -TypeName System.Drawing.Bitmap -ArgumentList $Width, $Height
    $graphics = [System.Drawing.Graphics]::FromImage($bmp)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    return @{ Bitmap = $bmp; Graphics = $graphics }
}

function Draw-BaseBackground {
    param(
        [System.Drawing.Graphics]$Graphics,
        [int]$Width,
        [int]$Height,
        [string]$BackgroundPath
    )
    $baseColor = Get-Color '#F7F1E8'
    $Graphics.Clear($baseColor)
    if ($BackgroundPath -and (Test-Path $BackgroundPath)) {
        $bg = [System.Drawing.Image]::FromFile($BackgroundPath)
        try {
            $Graphics.DrawImage($bg, 0, 0, $Width, $Height)
            $overlayBrush = New-Object -TypeName System.Drawing.SolidBrush -ArgumentList ([System.Drawing.Color]::FromArgb(184, 247, 241, 232))
            try {
                $Graphics.FillRectangle($overlayBrush, 0, 0, $Width, $Height)
            } finally {
                $overlayBrush.Dispose()
            }
        } finally {
            $bg.Dispose()
        }
    }
}

function New-WechatCover {
    param(
        [string]$OutputPath,
        [string]$BackgroundPath,
        [string]$Title,
        [string]$Subtitle
    )
    $canvas = New-Canvas -Width 900 -Height 383
    $bmp = $canvas.Bitmap
    $g = $canvas.Graphics
    try {
        Draw-BaseBackground -Graphics $g -Width 900 -Height 383 -BackgroundPath $BackgroundPath
        $panelBrush = New-Brush '#FFF8F0'
        $accentBrush = New-Brush '#F29F58'
        $textBrush = New-Brush '#20342E'
        $brandFont = New-Font -Size 18 -Bold $true
        $titleFont = New-Font -Size 34 -Bold $true
        $subFont = New-Font -Size 16
        try {
            Fill-RoundedRectangle -Graphics $g -Brush $panelBrush -X 40 -Y 40 -Width 510 -Height 300 -Radius 24
            $g.FillRectangle($accentBrush, 610, 70, 6, 238)
            $g.FillRectangle($accentBrush, 640, 70, 6, 180)
            $g.DrawString('AI趣创社', $brandFont, $accentBrush, 68, 74)
            $endY = Draw-WrappedText -Graphics $g -Text $Title -Font $titleFont -Brush $textBrush -X 68 -Y 118 -Width 440 -LineHeight 44 -MaxLines 3
            [void](Draw-WrappedText -Graphics $g -Text $Subtitle -Font $subFont -Brush $textBrush -X 70 -Y ([Math]::Max($endY + 8, 248)) -Width 420 -LineHeight 24 -MaxLines 3)
            Save-Png -Bitmap $bmp -Path $OutputPath
        } finally {
            $panelBrush.Dispose()
            $accentBrush.Dispose()
            $textBrush.Dispose()
            $brandFont.Dispose()
            $titleFont.Dispose()
            $subFont.Dispose()
        }
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
        [string]$Footer
    )
    $canvas = New-Canvas -Width 1200 -Height 900
    $bmp = $canvas.Bitmap
    $g = $canvas.Graphics
    try {
        $canvasColor = Get-Color '#FBF6EF'
        $g.Clear($canvasColor)
        $titleFont = New-Font -Size 30 -Bold $true
        $itemFont = New-Font -Size 20
        $footerFont = New-Font -Size 16
        $darkBrush = New-Brush '#20342E'
        $greenBrush = New-Brush '#2E5E4E'
        $orangeBrush = New-Brush '#F29F58'
        $panelBrush = New-Brush '#FFFDF9'
        $borderPen = New-Pen '#E8D7C4' 2
        try {
            $g.DrawString($Title, $titleFont, $darkBrush, 80, 70)
            $top = 180
            foreach ($item in $Items) {
                Fill-RoundedRectangle -Graphics $g -Brush $panelBrush -X 90 -Y $top -Width 1020 -Height 92 -Radius 18
                Draw-RoundedRectangle -Graphics $g -Pen $borderPen -X 90 -Y $top -Width 1020 -Height 92 -Radius 18
                $g.FillEllipse($orangeBrush, 120, $top + 24, 42, 42)
                $g.DrawString($item, $itemFont, $greenBrush, 190, $top + 28)
                $top += 110
            }
            $g.DrawString($Footer, $footerFont, $darkBrush, 92, 820)
            Save-Png -Bitmap $bmp -Path $OutputPath
        } finally {
            $titleFont.Dispose()
            $itemFont.Dispose()
            $footerFont.Dispose()
            $darkBrush.Dispose()
            $greenBrush.Dispose()
            $orangeBrush.Dispose()
            $panelBrush.Dispose()
            $borderPen.Dispose()
        }
    } finally {
        $g.Dispose()
        $bmp.Dispose()
    }
}

function New-XhsCard {
    param(
        [string]$OutputPath,
        [string]$Title,
        [string[]]$BodyLines,
        [string]$TagLine,
        [string]$BackgroundPath
    )
    $canvas = New-Canvas -Width 1242 -Height 1660
    $bmp = $canvas.Bitmap
    $g = $canvas.Graphics
    try {
        Draw-BaseBackground -Graphics $g -Width 1242 -Height 1660 -BackgroundPath $BackgroundPath
        $topBrush = New-Brush '#FFF8F0'
        $bodyBrush = New-Brush '#FFFDF9'
        $darkBrush = New-Brush '#20342E'
        $greenBrush = New-Brush '#2E5E4E'
        $orangeBrush = New-Brush '#F29F58'
        $tagTextBrush = New-Brush '#FFFDF9'
        $brandFont = New-Font -Size 22 -Bold $true
        $titleFont = New-Font -Size 48 -Bold $true
        $bodyFont = New-Font -Size 30
        $tagFont = New-Font -Size 22 -Bold $true
        try {
            Fill-RoundedRectangle -Graphics $g -Brush $topBrush -X 70 -Y 70 -Width 1102 -Height 340 -Radius 32
            Fill-RoundedRectangle -Graphics $g -Brush $bodyBrush -X 70 -Y 455 -Width 1102 -Height 1030 -Radius 32
            $g.DrawString('AI趣创社', $brandFont, $orangeBrush, 120, 112)
            [void](Draw-WrappedText -Graphics $g -Text $Title -Font $titleFont -Brush $darkBrush -X 118 -Y 170 -Width 900 -LineHeight 58 -MaxLines 4)

            $y = 540
            foreach ($line in $BodyLines) {
                if ([string]::IsNullOrWhiteSpace($line)) {
                    $y += 24
                    continue
                }
                if ($line.StartsWith('- ')) {
                    $g.FillEllipse($orangeBrush, 125, $y + 14, 14, 14)
                    $y = Draw-WrappedText -Graphics $g -Text $line.Substring(2) -Font $bodyFont -Brush $greenBrush -X 160 -Y $y -Width 900 -LineHeight 42 -MaxLines 3
                    $y += 28
                } else {
                    $y = Draw-WrappedText -Graphics $g -Text $line -Font $bodyFont -Brush $greenBrush -X 120 -Y $y -Width 960 -LineHeight 42 -MaxLines 4
                    $y += 28
                }
            }

            if ($TagLine) {
                Fill-RoundedRectangle -Graphics $g -Brush $orangeBrush -X 100 -Y 1520 -Width 500 -Height 70 -Radius 20
                $g.DrawString($TagLine, $tagFont, $tagTextBrush, 126, 1538)
            }

            Save-Png -Bitmap $bmp -Path $OutputPath
        } finally {
            $topBrush.Dispose()
            $bodyBrush.Dispose()
            $darkBrush.Dispose()
            $greenBrush.Dispose()
            $orangeBrush.Dispose()
            $tagTextBrush.Dispose()
            $brandFont.Dispose()
            $titleFont.Dispose()
            $bodyFont.Dispose()
            $tagFont.Dispose()
        }
    } finally {
        $g.Dispose()
        $bmp.Dispose()
    }
}

$wechatBase = Join-Path -Path $WechatDir -ChildPath 'images\wechat_cover_base.png'
$xhsBase = Join-Path -Path $XhsDir -ChildPath 'images\xhs_cover_base.png'

$wechatCoverOutput = Join-Path -Path $WechatDir -ChildPath 'images\01_公众号封面.png'

New-WechatCover `
    -OutputPath $wechatCoverOutput `
    -BackgroundPath $wechatBase `
    -Title '一套适合普通创作者的AI内容生产SOP' `
    -Subtitle '从选题到发布，怎么真正跑顺'

$wechatCards = @(
    @{
        File = '02_为什么用了AI还是没提效.png'
        Title = '为什么很多人用了 AI 还是没提效'
        Items = @(
            '今天写标题，明天换工具，后天又重写一遍',
            '看起来一直很忙，其实没有固定流程',
            '真正缺的不是工具，而是能反复跑起来的 SOP'
        )
        Footer = '先固定步骤，再让 AI 进入步骤里承担角色。'
    },
    @{
        File = '03_这套SOP适合哪些人.png'
        Title = '这套 SOP 最适合哪类创作者'
        Items = @(
            '一个人同时做小红书、公众号、朋友圈等图文内容',
            '每次写内容都像临场发挥，结构和节奏不稳定',
            '想用 AI 提速，但又不想把内容写成机器味'
        )
        Footer = '缺的不是更多工具，而是一条能反复跑顺的流程。'
    },
    @{
        File = '04_AI和人分别负责什么.png'
        Title = 'AI 和人，分别该负责什么'
        Items = @(
            'AI 负责：整理、扩展、提速、改写',
            '你负责：方向、取舍、观点、结论',
            '判断不外包，内容才不会越来越像机器'
        )
        Footer = 'AI 是提速器，不是判断替代者。'
    },
    @{
        File = '05_六步SOP总览.png'
        Title = '基础版内容生产 SOP：6 步跑顺'
        Items = @(
            '1. 拆受众问题',
            '2. 扩选题角度',
            '3. 搭文章提纲',
            '4. 写初稿并补表达',
            '5. 改成平台版本',
            '6. 补承接动作后发布'
        )
        Footer = '先把顺序固定，再逐步模板化。'
    },
    @{
        File = '06_前3步先跑顺.png'
        Title = '前 3 步先解决方向和结构'
        Items = @(
            '先拆清楚：写给谁，他们最常卡在哪',
            '围绕一个主题先铺出 5 到 10 个选题角度',
            '先定结论和提纲，再让 AI 进入写作阶段'
        )
        Footer = '前 3 步做扎实，后面才不会一直返工。'
    },
    @{
        File = '07_后3步决定能不能稳定.png'
        Title = '后 3 步决定能不能长期稳定产出'
        Items = @(
            '初稿出来后，自己补判断，不把观点外包',
            '同一套主逻辑，再改成小红书和公众号版本',
            '发布前补 CTA，让内容进入承接和转化'
        )
        Footer = '平台不同，表达不同，但底层逻辑可以共用。'
    },
    @{
        File = '08_发布前承接动作清单.png'
        Title = '发布前一定补上的 3 个承接动作'
        Items = @(
            '想清楚这篇内容希望读者下一步做什么',
            '在评论、私信、公众号沉淀里只选一个主 CTA',
            '检查 CTA 和正文是不是自然衔接，而不是硬塞'
        )
        Footer = '没有承接动作，内容很容易变成看过就算。'
    }
)

foreach ($card in $wechatCards) {
    $wechatOutput = Join-Path -Path $WechatDir -ChildPath ('images\' + $card.File)
    New-WechatDiagram `
        -OutputPath $wechatOutput `
        -Title $card.Title `
        -Items $card.Items `
        -Footer $card.Footer
}

$xhsCards = @(
    @{
        File = '01_首图.png'
        Title = '内容创作者先别急着学更多 AI'
        Body = @(
            '先搞懂这一条图文流程。',
            '流程跑顺了，产出才会稳。',
            '',
            '- 不是工具不够',
            '- 是步骤没固定'
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
        Title = '先看结论：这 6 步最值得先固定'
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
        Title = '前 2 步先解决选题和方向'
        Body = @(
            '1. 先拆受众痛点',
            '2. 再铺 5 到 10 个选题角度',
            '',
            '不要一上来就问 AI：',
            '“帮我写一篇。”'
        )
        Tag = '先定方向'
        Background = ''
    },
    @{
        File = '05_后三步.png'
        Title = '第 3 步最关键：先搭提纲'
        Body = @(
            '先定结论。',
            '再列 3 到 5 个要点。',
            '最后才写正文。',
            '',
            '提纲稳了，全文才不会散。'
        )
        Tag = '先提纲'
        Background = ''
    },
    @{
        File = '06_关键提醒.png'
        Title = '第 4 步和第 5 步：让 AI 提速，不替你判断'
        Body = @(
            '4. 初稿出来后，自己补判断',
            '5. 再改成不同平台版本',
            '',
            '- 小红书更短更快',
            '- 公众号更完整更解释'
        )
        Tag = '别外包判断'
        Background = ''
    },
    @{
        File = '07_CTA页.png'
        Title = '第 6 步：发前一定补 CTA'
        Body = @(
            '发之前先想清楚：',
            '你是要收藏、评论，',
            '还是私信领资料？',
            '',
            '一篇内容只留一个主动作。'
        )
        Tag = '发前检查'
        Background = ''
    },
    @{
        File = '08_最关键提醒.png'
        Title = '最关键的不是 AI 帮你写完'
        Body = @(
            '- AI 负责提速',
            '- 你负责方向',
            '- 你负责最终判断',
            '',
            '想看基础版清单，私信我 `流程`。'
        )
        Tag = '私信我 流程'
        Background = ''
    }
)

foreach ($card in $xhsCards) {
    $xhsOutput = Join-Path -Path $XhsDir -ChildPath ('images\' + $card.File)
    New-XhsCard `
        -OutputPath $xhsOutput `
        -Title $card.Title `
        -BodyLines $card.Body `
        -TagLine $card.Tag `
        -BackgroundPath $card.Background
}

