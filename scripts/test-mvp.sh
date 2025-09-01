#!/bin/bash

echo "🚀 Testing Minimum AI CAD MVP..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "📦 Building and starting services..."
docker-compose -f docker-compose.simple.yml up --build -d

echo "⏳ Waiting for services to start..."
sleep 15

echo "🔍 Checking service health..."

# Check API Gateway
echo "Checking API Gateway..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API Gateway is healthy"
else
    echo "❌ API Gateway is not responding"
fi

# Check File Processor
echo "Checking File Processor..."
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ File Processor is healthy"
else
    echo "❌ File Processor is not responding"
fi

# Check CAD Engine
echo "Checking CAD Engine..."
if curl -f http://localhost:8003/health > /dev/null 2>&1; then
    echo "✅ CAD Engine is healthy"
else
    echo "❌ CAD Engine is not responding"
fi

# Check Frontend
echo "Checking Frontend..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🎉 MVP Test Complete!"
echo ""
echo "🌐 Open your browser to: http://localhost:3000"
echo ""
echo "📝 To test the workflow:"
echo "1. Upload two STEP files (you can use any .step or .stp files)"
echo "2. Enter assembly instructions like 'connect with 5cm distance'"
echo "3. Click 'Generate Assembly'"
echo "4. Check the status and export options"
echo ""
echo "📊 Service URLs:"
echo "  - Frontend: http://localhost:3000"
echo "  - API Gateway: http://localhost:8000"
echo "  - File Processor: http://localhost:8001"  
echo "  - CAD Engine: http://localhost:8003"
echo ""
echo "🛑 To stop services: docker-compose -f docker-compose.simple.yml down"