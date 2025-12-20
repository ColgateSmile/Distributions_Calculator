# Fix all encoding issues in the HTML file
$file = "Chi_Square_Calculator.html"
$content = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)

# Replace all the corrupted unicode characters with proper ones
$replacements = @(
    ('‰¥', '≥'),
    ('áµ¢', 'ᵢ'),
    ('á±¼', '±'),
    ('Ã—', '×'),
    ('ˆ', '−'),
    ('€"', '—'),
    ('Ï‡Â²', 'χ²'),
    ('Î£Î£', 'ΣΣ'),
    ('†'', '→'),
    ('Î§Â²', 'Χ²'),
    ('Î±', 'α'),
    ('Â²', '²'),
    ('"', '"')
)

foreach ($pair in $replacements) {
    $content = $content.Replace($pair[0], $pair[1])
}

# Write back with UTF-8 no BOM
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($file, $content, $utf8NoBom)

Write-Host "Fixed all encoding issues!"
