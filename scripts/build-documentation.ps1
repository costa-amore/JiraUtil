# Build Documentation Functions
# This script contains functions for processing and packaging documentation during builds

function Convert-LinksForBuiltExecutable {
    <#
    .SYNOPSIS
    Converts relative links for built executable environment.
    
    .DESCRIPTION
    Converts relative documentation links to work in the built executable environment
    where README.md is in the root directory and docs are in a subdirectory.
    
    .PARAMETER Content
    The markdown content to process.
    
    .PARAMETER DocsFolderName
    The name of the docs folder in the built executable.
    
    .EXAMPLE
    $content = Convert-LinksForBuiltExecutable -Content $markdownContent -DocsFolderName "docs"
    #>
    
    param(
        [string]$Content,
        [string]$DocsFolderName = "docs"
    )
    
    # Convert relative links to docs/ format for built executable
    # (README.md is in root, so links need docs/ prefix)
    $Content = $Content -replace "\[Configuration Reference\]\(shared/configuration\.md\)", "[Configuration Reference]($DocsFolderName/shared/configuration.md)"
    $Content = $Content -replace "\[Command Examples Reference\]\(shared/command-examples\.md\)", "[Command Examples Reference]($DocsFolderName/shared/command-examples.md)"
    $Content = $Content -replace "\[Test Fixture Pattern Reference\]\(shared/test-fixture-pattern\.md\)", "[Test Fixture Pattern Reference]($DocsFolderName/shared/test-fixture-pattern.md)"
    $Content = $Content -replace "\[File Structure Reference\]\(shared/file-structure\.md\)", "[File Structure Reference]($DocsFolderName/shared/file-structure.md)"
    $Content = $Content -replace "\[Command Reference\]\(command-reference\.md\)", "[Command Reference]($DocsFolderName/command-reference.md)"
    $Content = $Content -replace "\[Troubleshooting Guide\]\(troubleshooting\.md\)", "[Troubleshooting Guide]($DocsFolderName/troubleshooting.md)"
    
    return $Content
}

function Add-VersionToMarkdown {
    <#
    .SYNOPSIS
    Adds version information to markdown content.
    
    .DESCRIPTION
    Adds a version section to markdown content if it doesn't already exist.
    
    .PARAMETER Content
    The markdown content to process.
    
    .PARAMETER Version
    The version string to add.
    
    .PARAMETER TitlePattern
    The title pattern to match for adding version after.
    
    .EXAMPLE
    $content = Add-VersionToMarkdown -Content $markdownContent -Version "1.0.0" -TitlePattern "# JiraUtil - User Guide"
    #>
    
    param(
        [string]$Content,
        [string]$Version,
        [string]$TitlePattern
    )
    
    if ($Content -notmatch "## Version") {
        $Content = $Content -replace $TitlePattern, "`$&`n`n## Version`n`nVersion: $Version"
    }
    
    return $Content
}

function New-DocumentationStructure {
    <#
    .SYNOPSIS
    Creates the documentation structure for built executables.
    
    .DESCRIPTION
    Creates the docs folder structure and processes all documentation files
    for the built executable package.
    
    .PARAMETER OutputDir
    The output directory for the built executable.
    
    .PARAMETER Version
    The version string to embed in documentation.
    
    .EXAMPLE
    New-DocumentationStructure -OutputDir "build-executables/Windows" -Version "1.0.0"
    #>
    
    param(
        [string]$OutputDir,
        [string]$Version
    )
    
    Write-Host "[DOCS] Creating documentation structure..." -ForegroundColor Yellow
    
    # Create docs folder structure
    New-Item -ItemType Directory -Path "$OutputDir\docs" -Force | Out-Null
    New-Item -ItemType Directory -Path "$OutputDir\docs\shared" -Force | Out-Null
    
    # Process main README (user guide)
    $UserReadme = Get-Content "docs\user-guide.md" -Raw
    $UserReadme = Add-VersionToMarkdown -Content $UserReadme -Version $Version -TitlePattern "# JiraUtil - User Guide"
    $UserReadme = Convert-LinksForBuiltExecutable -Content $UserReadme -DocsFolderName "docs"
    $UserReadme = $UserReadme.TrimEnd()
    $UserReadme | Out-File -FilePath "$OutputDir\README.md" -Encoding UTF8
    
    # Process command reference
    $CommandReadme = Get-Content "docs\command-reference.md" -Raw
    $CommandReadme = Add-VersionToMarkdown -Content $CommandReadme -Version $Version -TitlePattern "# Command Reference"
    # Fix navigation for user environment (remove references to dev-only files)
    $CommandReadme = $CommandReadme -replace "\[← Release and Versioning\]\(release-and-versioning\.md\)", "[← User Guide](../README.md)"
    $CommandReadme = $CommandReadme.TrimEnd()
    $CommandReadme | Out-File -FilePath "$OutputDir\docs\command-reference.md" -Encoding UTF8
    
    # Process troubleshooting guide
    $TroubleshootReadme = Get-Content "docs\troubleshooting.md" -Raw
    $TroubleshootReadme = Add-VersionToMarkdown -Content $TroubleshootReadme -Version $Version -TitlePattern "# Troubleshooting Guide"
    # Fix navigation for user environment (remove references to dev-only files)
    $TroubleshootReadme = $TroubleshootReadme -replace "\[User Guide →\]\(\.\./user-guide\.md\)", "[End of User Documentation]"
    $TroubleshootReadme = $TroubleshootReadme.TrimEnd()
    $TroubleshootReadme | Out-File -FilePath "$OutputDir\docs\troubleshooting.md" -Encoding UTF8
    
    # Process shared documentation files
    $SharedFiles = @("command-examples.md", "configuration.md", "file-structure.md", "test-fixture-pattern.md")
    foreach ($file in $SharedFiles) {
        $SourceFile = "docs\shared\$file"
        $TargetFile = "$OutputDir\docs\shared\$file"
        if (Test-Path $SourceFile) {
            $content = Get-Content $SourceFile -Raw
            # Add version after the title (first # heading) only if not already present
            if ($content -notmatch "## Version") {
                $content = $content -replace "^# [^`n]+", "`$&`n`n## Version`n`nVersion: $Version"
            }
            # Remove trailing blank lines
            $content = $content.TrimEnd()
            $content | Out-File -FilePath $TargetFile -Encoding UTF8
        }
    }
    
    Write-Host "[OK] Documentation structure created successfully" -ForegroundColor Green
}
