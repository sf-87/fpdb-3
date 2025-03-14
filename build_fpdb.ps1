# stop on error
$ErrorActionPreference = "Stop"

# define path to base
$BASE_PATH = Get-Location

# Name of the main script
$MAIN_SCRIPT = "fpdb.pyw"
$SECOND_SCRIPT = "HUD_main.pyw"

# Options of pyinstaller
$PYINSTALLER_OPTIONS = "--noconfirm --onedir --windowed --log-level=DEBUG"

# List of all files
$FILES = @(
    "Aux_Hud.py",
    "Configuration.py",
    "Database.py",
    "DerivedStats.py",
    "Exceptions.py",
    "Filters.py",
    "fpdb.pyw",
    "GuiAutoImport.py",
    "GuiBulkImport.py",
    "GuiCashGraphViewer.py",
    "GuiCashPlayerStats.py",
    "GuiCashSessionViewer.py",
    "GuiTourneyGraphViewer.py",
    "GuiTourneyPlayerStats.py",
    "Hand.py",
    "Hud.py",
    "HUD_config.xml",
    "HUD_main.pyw",
    "Importer.py",
    "interlocks.py",
    "logging.conf",
    "PokerStarsStructures.py",
    "PokerStarsSummary.py",
    "PokerStarsToFpdb.py",
    "SQL.py",
    "Stats.py",
    "TableWindow.py",
    "tribal.jpg"
)

# Function to generate the pyinstaller command
function Generate-PyInstallerCommand {
    param (
        [string]$scriptPath
    )

    $command = "pyinstaller $PYINSTALLER_OPTIONS"

    # add icon
    $command += " --icon=`"$BASE_PATH\tribal.jpg`""

    # process files
    foreach ($file in $FILES) {
        $command += " --add-data `"$BASE_PATH\$file;.`""
    }

    $command += " `"$BASE_PATH\$scriptPath`""

    return $command
}

# Function to copy HUD_main.exe
function Copy-HUDMain {
    param (
        [string]$sourceDir,
        [string]$targetDir
    )

    $hudMainExe = Join-Path -Path $sourceDir -ChildPath "HUD_main.exe"
    $targetExe = Join-Path -Path $targetDir -ChildPath "HUD_main.exe"

    if (-not (Test-Path -Path $targetExe)) {
        Write-Output "Copy HUD_main.exe from $hudMainExe to $targetExe"
        Copy-Item -Path $hudMainExe -Destination $targetExe -Force
    }
}

# Generate the pyinstaller command for the main script
$command = Generate-PyInstallerCommand -scriptPath $MAIN_SCRIPT
Write-Output "Execution : $command"
Invoke-Expression $command

# Generate the pyinstaller command for the second script
$command = Generate-PyInstallerCommand -scriptPath $SECOND_SCRIPT
Write-Output "Execution : $command"
Invoke-Expression $command

Write-Output "Build success"

$fpdbOutputDir = Join-Path -Path $BASE_PATH -ChildPath "dist/fpdb"
$hudOutputDir = Join-Path -Path $BASE_PATH -ChildPath "dist/HUD_main"

Copy-HUDMain -sourceDir $hudOutputDir -targetDir $fpdbOutputDir

Write-Output "Move success"
