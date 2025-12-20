#!/bin/bash
# Script to deploy the app to Railway

# Exit on error
set -e

# Check for Railway CLI
if ! command -v railway &> /dev/null; then
    echo "Railway CLI not found. Installing..."
    npm install -g railway
fi

# Login to Railway (interactive)
echo "Logging in to Railway..."
#railway login

# Check if project is linked, if not, create it
if ! railway status &> /dev/null; then
    echo "No linked project found. Creating a new project..."
    
    # Get project name from user or use default
    read -p "Enter project name (or press Enter for 'bigschool-module5'): " project_name
    if [[ -z "$project_name" ]]; then
        project_name="bigschool-module5"
    fi
    
    echo "Creating new Railway project: $project_name"
    railway init --name "$project_name"
    
    # Wait a moment for project creation
    sleep 2
    
    echo "Project created successfully!"
fi

# Check if service is linked, if not, create or link one
service_status=$(railway status | grep "Service:" | awk '{print $2}')
if [[ "$service_status" == "None" ]]; then
    echo "No service linked. You need to link or create a service."
    echo "Options:"
    echo "1. Create a new service"
    echo "2. Link to an existing service"
    
    read -p "Choose option (1 or 2): " choice
    
    case $choice in
        1)
            read -p "Enter service name (or press Enter for 'web-service'): " service_name
            if [[ -z "$service_name" ]]; then
                service_name="web-service"
            fi
            echo "Creating new service: $service_name"
            railway add --service "$service_name" --variables "OPENAI_API_KEY=$OPENAI_API_KEY"
            ;;
        2)
            echo "Listing services in this project..."
            railway status
            read -p "Enter the service name to link: " service_name
            railway service "$service_name"
            ;;
        *)
            echo "Invalid choice. Creating a default web service..."
            railway add --service "web-service"
            ;;
    esac
    
    echo "Service linked successfully!"
fi

# Deploy the project
echo "Deploying to Railway..."

# Deploy the service
echo "Starting deployment..."
railway up --detach

echo "Deployment complete!"
echo "🌐 Your app will be available at the Railway-provided URL"

echo "Creating/Fetching Railway domain..."
railway domain