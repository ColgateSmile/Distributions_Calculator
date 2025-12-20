# Read file as raw text
$filePath = 'Chi_Square_Calculator.html'
$text = [System.IO.File]::ReadAllText($filePath, [System.Text.Encoding]::UTF8)

# Replace corrupted encoding patterns with ASCII-safe versions
$text = $text -replace [regex]::Escape('€"'), ' - '
$text = $text -replace [regex]::Escape('Ï‡Â²'), 'chi-square'
$text = $text -replace [regex]::Escape('Î£Î£'), 'Sum'
$text = $text -replace [regex]::Escape('Î§Â²'), 'ChiSq'
$text = $text -replace [regex]::Escape('Î±'), 'alpha'
$text = $text -replace [regex]::Escape('áµ¢'), 'i'
$text = $text -replace [regex]::Escape('±¼'), 'j'
$text = $text -replace [regex]::Escape('Ã—'), '*'
$text = $text -replace [regex]::Escape('Ã '), '*'
$text = $text -replace [regex]::Escape('ˆ''), '-'
$text = $text -replace [regex]::Escape('Â²'), '^2'
$text = $text -replace [regex]::Escape('Â'), ''
$text = $text -replace [regex]::Escape('‰¥'), '>='
$text = $text -replace [regex]::Escape('†''), '->'
$text = $text -replace [regex]::Escape('ˆ'), '-'
$text = $text -replace [regex]::Escape('Ã'), ''

# Write back as UTF-8 without BOM
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($filePath, $text, $utf8NoBom)

Write-Host 'Fixed encoding issues - file rewritten as clean UTF-8'
Write-Host "File size: $((Get-Item $filePath).Length) bytes"
