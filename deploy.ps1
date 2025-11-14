# Notion Bot API Deployment Script (PowerShell)
# This script automates the deployment of the Notion Bot API application

# Set error handling
$ErrorActionPreference = "Stop"

# Colors for output
$Green = [System.ConsoleColor]::Green
$Red = [System.ConsoleColor]::Red
$Yellow = [System.ConsoleColor]::Yellow
$Blue = [System.ConsoleColor]::Blue
$White = [System.ConsoleColor]::White

# Default configuration
$Environment = "dev"
$DockerComposeFile = "docker-compose.yml"
$DockerComposeProdFile = "docker-compose.prod.yml"
$EnvFile = ".env"

# Function to print colored output
function Write-Info {
    param([string]$Message)
    Write-Host "INFO: $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "SUCCESS: $Message" -ForegroundColor $Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "WARN: $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "ERROR: $Message" -ForegroundColor $Red
}

# Function to check prerequisites
function Check-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check Docker
    try {
        docker --version | Out-Null
    } catch {
        Write-Error "Docker is not installed or not in PATH. Please install Docker Desktop before running this script."
        exit 1
    }
    
    # Check Docker Compose
    try {
        docker-compose --version | Out-Null
    } catch {
        Write-Error "Docker Compose is not installed or not in PATH. Please ensure Docker Desktop includes Docker Compose."
        exit 1
    }
    
    # Check for .env file
    if (!(Test-Path $EnvFile)) {
        Write-Info "Environment file ($EnvFile) not found. Creating from example..."
        if (Test-Path "$EnvFile.example") {
            Copy-Item "$EnvFile.example" $EnvFile
            Write-Success "Created $EnvFile from example. Please update it with your Notion API key before deployment."
            exit 0
        } else {
            Write-Error "Neither $EnvFile nor $EnvFile.example found. Cannot proceed."
            exit 1
        }
    }
    
    Write-Success "All prerequisites met."
}

# Function to validate environment configuration
function Validate-Env {
    Write-Info "Validating environment configuration..."
    
    # Read the environment file
    $envContent = Get-Content $EnvFile -Raw
    
    # Check if NOTION_API_KEY is set
    if ($envContent -notmatch "^NOTION_API_KEY=.*" -or $envContent -match "^NOTION_API_KEY=$" -or $envContent -match "^NOTION_API_KEY=secret_") {
        Write-Warn "NOTION_API_KEY is not set or has default value in $EnvFile"
        $confirm = Read-Host "Do you want to continue anyway? (y/N)"
        if ($confirm -ne 'y' -and $confirm -ne 'Y') {
            Write-Info "Please update $EnvFile with your Notion API key and run again."
            exit 1
        }
    }
    
    Write-Success "Environment configuration validated."
}

# Function to build and start services
function Deploy-Services {
    Write-Info "Building and starting Notion Bot API services..."
    
    if ($Environment -eq "prod") {
        $ComposeFile = $DockerComposeProdFile
        $ComposeEnvFile = "$EnvFile.prod"
        
        if (!(Test-Path $ComposeEnvFile)) {
            Write-Error "Production environment file $ComposeEnvFile not found."
            exit 1
        }
        
        Write-Info "Using production compose file: $ComposeFile with environment: $ComposeEnvFile"
        docker-compose -f $ComposeFile --env-file $ComposeEnvFile up -d --build
    } else {
        Write-Info "Using development compose file: $DockerComposeFile"
        docker-compose -f $DockerComposeFile up -d --build
    }
    
    Write-Info "Services started. Waiting for health check..."
    
    # Wait for services to be healthy
    $maxAttempts = 30
    $attempt = 1
    $healthy = $false
    
    while ($attempt -le $maxAttempts -and -not $healthy) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
            if ($response.status -eq "healthy") {
                $healthy = $true
                Write-Success "API is healthy after $attempt attempts."
            }
        } catch {
            Write-Info "Waiting for API to be healthy... ($attempt/$maxAttempts)"
        }
        
        if (-not $healthy) {
            Start-Sleep -Seconds 10
            $attempt++
        }
    }
    
    if (-not $healthy) {
        Write-Error "API did not become healthy within the timeout period."
        docker-compose logs
        exit 1
    }
}

# Function to run tests to verify deployment
function Verify-Deployment {
    Write-Info "Verifying deployment..."
    
    # Test health endpoint
    try {
        $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
        if ($healthResponse.status -eq "healthy") {
            Write-Success "Health check passed."
        } else {
            Write-Error "Health check failed."
            exit 1
        }
    } catch {
        Write-Error "Health check failed: $_"
        exit 1
    }
    
    # Test root endpoint
    try {
        $rootResponse = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 5
        if ($rootResponse.Content -match "Notion Bot API") {
            Write-Success "Root endpoint check passed."
        } else {
            Write-Error "Root endpoint check failed."
            exit 1
        }
    } catch {
        Write-Error "Root endpoint check failed: $_"
        exit 1
    }
    
    # Check if Docker services are running
    $services = docker-compose ps --format "table {{.Name}}\t{{.State}}"
    if ($services -match "Up") {
        Write-Success "All services are running."
    } else {
        Write-Error "Some services may not be running properly."
        Write-Host $services
        exit 1
    }
}

# Function to display deployment information
function Display-Info {
    Write-Success "=" * 40
    Write-Host "Notion Bot API Deployment Complete" -ForegroundColor Green
    Write-Success "=" * 40
    Write-Host ""
    Write-Info "API Endpoints:"
    Write-Info "  - Main API: http://localhost:8000"
    Write-Info "  - API Documentation: http://localhost:8000/docs"
    Write-Info "  - Health Check: http://localhost:8000/health"
    Write-Host ""
    Write-Info "Docker Services Status:"
    docker-compose ps
    Write-Host ""
    Write-Info "To view logs: docker-compose logs -f"
    Write-Info "To stop services: docker-compose down"
    Write-Host ""
    Write-Success "Deployment completed successfully!"
}

# Function to display help
function Display-Help {
    Write-Host "Notion Bot API Deployment Script (PowerShell)"
    Write-Host ""
    Write-Host "Usage: $PSCommandPath [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -h, --help     Display this help message"
    Write-Host "  -e, --env      Environment to deploy (dev/prod) - default: dev"
    Write-Host "  --stop         Stop running services"
    Write-Host "  --restart      Restart services"
    Write-Host "  --logs         View service logs"
    Write-Host "  --status       Check service status"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  $PSCommandPath                    # Deploy in development mode"
    Write-Host "  $PSCommandPath -e prod            # Deploy in production mode"
    Write-Host "  $PSCommandPath --stop             # Stop services"
    Write-Host "  $PSCommandPath --restart          # Restart services"
    Write-Host "  $PSCommandPath --logs             # View logs"
    Write-Host ""
}

# Main function to handle command line arguments
function Main {
    param(
        [string]$env = "dev",
        [switch]$help = $false,
        [switch]$stop = $false,
        [switch]$restart = $false,
        [switch]$logs = $false,
        [switch]$status = $false
    )
    
    if ($help) {
        Display-Help
        return
    }
    
    # Determine action based on switches
    $action = "deploy"
    if ($stop) { $action = "stop" }
    elseif ($restart) { $action = "restart" }
    elseif ($logs) { $action = "logs" }
    elseif ($status) { $action = "status" }
    
    # Set environment if provided
    if ($env -ne "dev") {
        $Global:Environment = $env
    }
    
    # Execute the appropriate action
    switch ($action) {
        "deploy" {
            Write-Info "Starting Notion Bot API deployment in $Global:Environment mode..."
            Check-Prerequisites
            Validate-Env
            Deploy-Services
            Verify-Deployment
            Display-Info
        }
        "stop" {
            Write-Info "Stopping Notion Bot API services..."
            docker-compose down
            Write-Success "Services stopped."
        }
        "restart" {
            Write-Info "Restarting Notion Bot API services..."
            docker-compose down
            # Recursively call main with deploy action
            Main -env $Global:Environment
        }
        "logs" {
            Write-Info "Showing service logs..."
            docker-compose logs -f
        }
        "status" {
            Write-Info "Checking service status..."
            docker-compose ps
        }
    }
}

# Parse arguments and call main
$argList = @()
if ($args) {
    foreach ($arg in $args) {
        if ($arg -eq "-h" -or $arg -eq "--help") {
            Display-Help
            exit 0
        } elseif ($arg -eq "--stop") {
            $argList += "-stop"
        } elseif ($arg -eq "--restart") {
            $argList += "-restart"
        } elseif ($arg -eq "--logs") {
            $argList += "-logs"
        } elseif ($arg -eq "--status") {
            $argList += "-status"
        } elseif ($arg -eq "-e" -or $arg -eq "--env") {
            # Next argument should be the environment
            continue
        } elseif ($arg -match "^(dev|prod)$") {
            $argList += "-env", $arg
        } elseif ($arg -match "^--env=(dev|prod)$") {
            $envValue = $arg -replace "^--env=", ""
            $argList += "-env", $envValue
        }
    }
}

# Call main with parsed arguments
Main @argList