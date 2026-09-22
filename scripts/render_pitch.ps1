$ErrorActionPreference = 'Stop'
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$presentationFile = Join-Path $projectRoot 'Projeto_Final_Artefatos\InsurMinds_Projeto_Final.pptx'
$renderDir = Join-Path $projectRoot 'tmp\slides'
New-Item -ItemType Directory -Force -Path $renderDir | Out-Null
$presentationApp = New-Object -ComObject PowerPoint.Application
$deck = $null
try {
    $deck = $presentationApp.Presentations.Open($presentationFile, -1, 0, 0)
    $deck.Export($renderDir, 'PNG', 1280, 720)
    Write-Output "Slides renderizados: $($deck.Slides.Count)"
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if ($presentationApp.Presentations.Count -eq 0) { $presentationApp.Quit() }
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($presentationApp) | Out-Null
}
