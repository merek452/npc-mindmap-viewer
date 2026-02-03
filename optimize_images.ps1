# Image Optimization Script for NPC Mind Map
# Converts and optimizes all portrait images

Write-Host "NPC Portrait Image Optimizer" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$sourceFolder = "Images"
$outputFolder = "Images_optimized"
$maxSize = 500

# Check if source folder exists
if (-not (Test-Path $sourceFolder)) {
    Write-Host "ERROR: Images folder not found!" -ForegroundColor Red
    Write-Host "Please run this script from the mindmap_viewer directory." -ForegroundColor Yellow
    exit 1
}

# Create output folder
Write-Host "Creating output folder..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $outputFolder | Out-Null

# Get all image files
$imageFiles = Get-ChildItem $sourceFolder -File | Where-Object { 
    $_.Extension -match '\.(png|jpg|jpeg|bmp|gif)$' 
}

$nonImageFiles = Get-ChildItem $sourceFolder -File | Where-Object { 
    $_.Extension -notmatch '\.(png|jpg|jpeg|bmp|gif)$' 
}

Write-Host "Found:" -ForegroundColor Cyan
Write-Host "  - $($imageFiles.Count) image files" -ForegroundColor Green
Write-Host "  - $($nonImageFiles.Count) non-image files" -ForegroundColor Yellow
Write-Host ""

# Calculate current size
$currentSize = ($imageFiles | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Current total size: $([math]::Round($currentSize, 2)) MB" -ForegroundColor Yellow
Write-Host ""

# Check if ImageMagick is available
$hasImageMagick = $null -ne (Get-Command magick -ErrorAction SilentlyContinue)

if ($hasImageMagick) {
    Write-Host "ImageMagick detected - using high-quality conversion" -ForegroundColor Green
} else {
    Write-Host "ImageMagick not found - using Windows .NET" -ForegroundColor Yellow
    Write-Host "For best results: winget install ImageMagick.ImageMagick" -ForegroundColor Yellow
}
Write-Host ""

# Process each image
$processed = 0
$errors = 0

foreach ($file in $imageFiles) {
    $processed++
    $outputFile = Join-Path $outputFolder "$($file.BaseName).png"
    
    Write-Host "[$processed/$($imageFiles.Count)] Processing: $($file.Name)" -NoNewline
    
    try {
        if ($hasImageMagick) {
            $result = magick convert "$($file.FullName)" -resize "${maxSize}x${maxSize}>" -strip -quality 90 "$outputFile" 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host " [OK]" -ForegroundColor Green
            } else {
                Write-Host " [FAILED]" -ForegroundColor Red
                $errors++
            }
        } else {
            Add-Type -AssemblyName System.Drawing
            
            $img = [System.Drawing.Image]::FromFile($file.FullName)
            
            $ratio = [math]::Min($maxSize / $img.Width, $maxSize / $img.Height)
            if ($ratio -lt 1) {
                $newWidth = [int]($img.Width * $ratio)
                $newHeight = [int]($img.Height * $ratio)
            } else {
                $newWidth = $img.Width
                $newHeight = $img.Height
            }
            
            $newImg = New-Object System.Drawing.Bitmap($newWidth, $newHeight)
            $graphics = [System.Drawing.Graphics]::FromImage($newImg)
            $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $graphics.DrawImage($img, 0, 0, $newWidth, $newHeight)
            
            $newImg.Save($outputFile, [System.Drawing.Imaging.ImageFormat]::Png)
            
            $graphics.Dispose()
            $newImg.Dispose()
            $img.Dispose()
            
            Write-Host " [OK]" -ForegroundColor Green
        }
    } catch {
        Write-Host " [ERROR: $_]" -ForegroundColor Red
        $errors++
    }
}

# Move non-image files
if ($nonImageFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "Moving non-image files to parent directory..." -ForegroundColor Yellow
    foreach ($file in $nonImageFiles) {
        try {
            Move-Item $file.FullName ".." -Force
            Write-Host "  Moved: $($file.Name)" -ForegroundColor Gray
        } catch {
            Write-Host "  Could not move: $($file.Name)" -ForegroundColor Yellow
        }
    }
}

# Calculate new size
$newFiles = Get-ChildItem $outputFolder -File
$newSize = ($newFiles | Measure-Object -Property Length -Sum).Sum / 1MB

# Summary
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "OPTIMIZATION COMPLETE" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Results:" -ForegroundColor Cyan
Write-Host "  Original size:  $([math]::Round($currentSize, 2)) MB" -ForegroundColor Yellow
Write-Host "  Optimized size: $([math]::Round($newSize, 2)) MB" -ForegroundColor Green
Write-Host "  Savings:        $([math]::Round($currentSize - $newSize, 2)) MB ($([math]::Round((1 - $newSize/$currentSize) * 100, 1))%)" -ForegroundColor Green
Write-Host "  Processed:      $processed files" -ForegroundColor Gray

if ($errors -gt 0) {
    Write-Host "  Errors:         $errors files" -ForegroundColor Red
}

Write-Host ""
Write-Host "Folders:" -ForegroundColor Cyan
Write-Host "  Optimized: $outputFolder\" -ForegroundColor Green
Write-Host "  Original:  $sourceFolder\ (unchanged)" -ForegroundColor Yellow

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Check optimized images in '$outputFolder' folder" -ForegroundColor White
Write-Host "  2. If good, run: .\replace_images.ps1" -ForegroundColor Green
Write-Host ""
Write-Host "Done!" -ForegroundColor Green
