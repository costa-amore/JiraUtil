#!/usr/bin/env pwsh
<#
.SYNOPSIS
    PowerShell wrapper for the Python color system to ensure consistency across all scripts.

.DESCRIPTION
    This module provides PowerShell functions that reuse the Python color system
    to ensure consistent coloring and prevent duplication of color definitions.
    Uses enum-like structure to prevent typos and ensure consistency.
#>

# =============================================================================
# COLOR ENUM-LIKE STRUCTURE
# =============================================================================

# Define color tags as a hashtable to prevent typos and ensure consistency
$script:ColorTags = @{
    # Success/Positive messages (Green)
    SUCCESS = "[SUCCESS]"
    OK = "[OK]"
    
    # Error/Failure messages (Red)
    FAIL = "[FAIL]"
    ERROR = "[ERROR]"
    MISSING = "[MISSING]"
    
    # Warning messages (Orange/Yellow)
    WARN = "[WARN]"
    
    # Information messages (Blue)
    INFO = "[INFO]"
    TEST = "[TEST]"
    FILES = "[FILES]"
    SEARCH = "[SEARCH]"
    CSV = "[CSV]"
    CLI = "[CLI]"
    AUTH = "[AUTH]"
    ARCH = "[ARCH]"
    PERF = "[PERF]"
    FUNC = "[FUNC]"
    RUN = "[RUN]"
    TIP = "[TIP]"
    RETRY = "[RETRY]"
    COLOR = "[COLOR]"
    
    # Build/Process messages (Yellow)
    BUILD = "[BUILD]"
    GIT = "[GIT]"
    TAG = "[TAG]"
    
    # Version messages (Green)
    VERSION = "[VERSION]"
    
    # Link messages (Blue)
    LINK = "[LINK]"
}

# =============================================================================
# CORE FUNCTIONS
# =============================================================================

function Write-TaggedMessage {
    <#
    .SYNOPSIS
        Write a message with consistent color coding using the Python color system.
    
    .PARAMETER Message
        The message to display (should include the tag like [INFO], [FAIL], etc.)
    
    .PARAMETER Tag
        The tag type from the ColorTags enum (prevents typos)
    
    .EXAMPLE
        Write-TaggedMessage "This is an info message" $ColorTags.INFO
        Write-TaggedMessage "This is an error message" $ColorTags.FAIL
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [string]$Tag = $ColorTags.INFO
    )
    
    # Validate tag exists
    if ($Tag -notin $ColorTags.Values) {
        Write-Warning "Invalid tag '$Tag'. Using default INFO tag."
        $Tag = $ColorTags.INFO
    }
    
    # Use Python to get the colored text
    # Create a temporary file to avoid quoting issues
    $tempFile = [System.IO.Path]::GetTempFileName()
    $pythonScript = @"
import sys
sys.path.insert(0, 'src')
from utils.colors import get_colored_text
print(get_colored_text("$Tag $Message"), end='')
"@
    $pythonScript | Out-File -FilePath $tempFile -Encoding UTF8
    $coloredMessage = python -u $tempFile
    Remove-Item $tempFile
    
    # Write the colored message
    Write-Host $coloredMessage
}

function Write-TaggedMessageNoNewline {
    <#
    .SYNOPSIS
        Write a message with consistent color coding without a newline.
    
    .PARAMETER Message
        The message to display
    
    .PARAMETER Tag
        The tag type from the ColorTags enum (prevents typos)
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [string]$Tag = $ColorTags.INFO
    )
    
    # Validate tag exists
    if ($Tag -notin $ColorTags.Values) {
        Write-Warning "Invalid tag '$Tag'. Using default INFO tag."
        $Tag = $ColorTags.INFO
    }
    
    # Use Python to get the colored text
    # Create a temporary file to avoid quoting issues
    $tempFile = [System.IO.Path]::GetTempFileName()
    $pythonScript = @"
import sys
sys.path.insert(0, 'src')
from utils.colors import get_colored_text
print(get_colored_text("$Tag $Message"), end='')
"@
    $pythonScript | Out-File -FilePath $tempFile -Encoding UTF8
    $coloredMessage = python -u $tempFile
    Remove-Item $tempFile
    
    # Write the colored message without newline
    Write-Host $coloredMessage -NoNewline
}

# =============================================================================
# CONVENIENCE FUNCTIONS (Using enum-like approach)
# =============================================================================

function Write-Info {
    param([string]$Message)
    Write-TaggedMessage $Message $ColorTags.INFO
}

function Write-Success {
    param([string]$Message)
    Write-TaggedMessage $Message $ColorTags.SUCCESS
}

function Write-OK {
    param([string]$Message)
    Write-TaggedMessage $Message $ColorTags.OK
}

function Write-Fail {
    param([string]$Message)
    Write-TaggedMessage $Message $ColorTags.FAIL
}

function Write-Error {
    param([string]$Message)
    Write-TaggedMessage $Message $ColorTags.ERROR
}

function Write-Warn {
    param([string]$Message)
    Write-TaggedMessage $Message $ColorTags.WARN
}

function Write-Build {
    param([string]$Message)
    Write-TaggedMessage $Message $ColorTags.BUILD
}

function Write-Git {
    param([string]$Message)
    Write-TaggedMessage $Message $ColorTags.GIT
}

function Write-Tag {
    param([string]$Message)
    Write-TaggedMessage $Message $ColorTags.TAG
}

function Write-Version {
    param([string]$Message)
    Write-TaggedMessage $Message $ColorTags.VERSION
}

function Write-Link {
    param([string]$Message)
    Write-TaggedMessage $Message $ColorTags.LINK
}

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

function Test-ValidTag {
    <#
    .SYNOPSIS
        Test if a tag is valid according to the ColorTags enum.
    
    .PARAMETER Tag
        The tag to validate (e.g., $ColorTags.INFO, $ColorTags.FAIL)
    
    .RETURNS
        Boolean indicating if the tag is valid
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Tag
    )
    
    return $Tag -in $ColorTags.Values
}

function Get-ValidTags {
    <#
    .SYNOPSIS
        Get all valid tags from the ColorTags enum.
    
    .RETURNS
        Array of valid tags
    #>
    return $ColorTags.Values
}

function Get-ColorTagsEnum {
    <#
    .SYNOPSIS
        Get the ColorTags hashtable for direct access.
    
    .RETURNS
        Hashtable containing all color tags
    #>
    return $ColorTags
}

# Functions and variables are available when dot-sourced
