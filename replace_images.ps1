# Image Replacement Script
# Safely replaces original images with optimized versions

Write-Host "🔄 Image Replacement Script" -ForegroundColor Cyan
Write-Host "===========================`n" -ForegroundColor Cyan

$sourceFolder = "Images"
$optimizedFolder = "Images_optimized"
$backupFolder = "Images_backup"

# Check if optimized folder exists
if (-not (Test-Path $optimizedFolder)) {
    Write-Host "❌ Error: $optimizedFolder folder not found!" -ForegroundColor Red
    Write-Host "Please run optimize_images.ps1 first." -ForegroundColor Yellow
    exit 1
}

# Check if source folder exists
if (-not (Test-Path $sourceFolder)) {
    Write-Host "❌ Error: $sourceFolder folder not found!" -ForegroundColor Red
    exit 1
}

# Confirm replacement
Write-Host "This will:" -ForegroundColor Yellow
Write-Host "  1. Rename '$sourceFolder' → '$backupFolder'" -ForegroundColor Gray
Write-Host "  2. Rename '$optimizedFolder' → '$sourceFolder'" -ForegroundColor Gray
Write-Host "  3. Keep backup for safety`n" -ForegroundColor Gray

$confirm = Read-Host "Continue? (yes/no)"

if ($confirm -ne "yes") {
    Write-Host "`n❌ Cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host "`n🔄 Replacing images..." -ForegroundColor Yellow

try {
    # Backup original
    if (Test-Path $backupFolder) {
        Write-Host "⚠️  Backup folder already exists, removing old backup..." -ForegroundColor Yellow
        Remove-Item $backupFolder -Recurse -Force
    }
    
    Write-Host "📦 Creating backup: $sourceFolder → $backupFolder" -ForegroundColor Gray
    Rename-Item $sourceFolder $backupFolder
    
    # Use optimized as new Images folder
    Write-Host "📁 Installing optimized: $optimizedFolder → $sourceFolder" -ForegroundColor Gray
    Rename-Item $optimizedFolder $sourceFolder
    
    Write-Host "`n✅ SUCCESS!" -ForegroundColor Green
    Write-Host "`n📊 Summary:" -ForegroundColor Cyan
    Write-Host "   New Images folder: Ready to use" -ForegroundColor Green
    Write-Host "   Backup folder:     $backupFolder (keep until tested)" -ForegroundColor Yellow
    
    Write-Host "`n🎯 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Open npc_mindmap_viewer.html in browser" -ForegroundColor White
    Write-Host "   2. Check that NPC portraits look good" -ForegroundColor White
    Write-Host "   3. Test a few NPCs with images" -ForegroundColor White
    Write-Host "   4. If all looks good, delete backup:" -ForegroundColor White
    Write-Host "      Remove-Item $backupFolder -Recurse" -ForegroundColor Gray
    
} catch {
    Write-Host "`n❌ Error during replacement: $_" -ForegroundColor Red
    Write-Host "Your original Images folder is safe." -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✅ Done!" -ForegroundColor Green
