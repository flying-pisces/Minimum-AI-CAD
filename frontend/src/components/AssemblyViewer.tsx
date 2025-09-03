import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';
import { AssemblyResult } from '../types/assembly';

interface AssemblyViewerProps {
  assembly: AssemblyResult;
  width?: number;
  height?: number;
}

export const AssemblyViewer: React.FC<AssemblyViewerProps> = ({ 
  assembly, 
  width = 600, 
  height = 400 
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);

  useEffect(() => {
    if (!mountRef.current) return;
    
    const mountElement = mountRef.current;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf5f5f5);
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(100, 100, 100);
    camera.lookAt(0, 0, 0);

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    rendererRef.current = renderer;
    mountElement.appendChild(renderer.domElement);

    // Enhanced lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
    scene.add(ambientLight);

    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight1.position.set(50, 50, 25);
    directionalLight1.castShadow = true;
    scene.add(directionalLight1);

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.3);
    directionalLight2.position.set(-50, 50, -25);
    scene.add(directionalLight2);

    // Grid
    const gridHelper = new THREE.GridHelper(200, 20, 0xcccccc, 0xeeeeee);
    scene.add(gridHelper);

    // Axes helper
    const axesHelper = new THREE.AxesHelper(30);
    scene.add(axesHelper);

    // Controls (enhanced orbit controls simulation)
    let mouseDown = false;
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;
    let currentX = 0;
    let currentY = 0;

    const onMouseDown = (event: MouseEvent) => {
      mouseDown = true;
      mouseX = event.clientX;
      mouseY = event.clientY;
    };

    const onMouseUp = () => {
      mouseDown = false;
    };

    const onMouseMove = (event: MouseEvent) => {
      if (!mouseDown) return;

      const deltaX = event.clientX - mouseX;
      const deltaY = event.clientY - mouseY;

      targetX += deltaX * 0.01;
      targetY += deltaY * 0.01;
      targetY = Math.max(-Math.PI/2 + 0.1, Math.min(Math.PI/2 - 0.1, targetY));

      mouseX = event.clientX;
      mouseY = event.clientY;
    };

    const onWheel = (event: WheelEvent) => {
      event.preventDefault();
      const scale = event.deltaY > 0 ? 1.1 : 0.9;
      camera.position.multiplyScalar(scale);
      camera.position.x = Math.max(-500, Math.min(500, camera.position.x));
      camera.position.y = Math.max(-500, Math.min(500, camera.position.y));
      camera.position.z = Math.max(-500, Math.min(500, camera.position.z));
    };

    const canvas = renderer.domElement;
    canvas.addEventListener('mousedown', onMouseDown);
    canvas.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('wheel', onWheel);

    // Smooth camera animation
    const updateCamera = () => {
      currentX += (targetX - currentX) * 0.05;
      currentY += (targetY - currentY) * 0.05;

      const radius = camera.position.length();
      camera.position.x = radius * Math.cos(currentY) * Math.cos(currentX);
      camera.position.y = radius * Math.sin(currentY);
      camera.position.z = radius * Math.cos(currentY) * Math.sin(currentX);
      camera.lookAt(0, 0, 0);
    };

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      updateCamera();
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      canvas.removeEventListener('mousedown', onMouseDown);
      canvas.removeEventListener('mouseup', onMouseUp);
      canvas.removeEventListener('mousemove', onMouseMove);
      canvas.removeEventListener('wheel', onWheel);
      if (mountElement && renderer.domElement) {
        mountElement.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [width, height]);

  useEffect(() => {
    if (!assembly || !sceneRef.current) return;

    // Clear previous assembly
    const objectsToRemove = sceneRef.current.children.filter(
      child => child.userData.isAssemblyPart
    );
    objectsToRemove.forEach(obj => sceneRef.current!.remove(obj));

    // Create assembly visualization
    const assemblyGroup = createAssemblyVisualization(assembly);
    assemblyGroup.userData.isAssemblyPart = true;
    sceneRef.current.add(assemblyGroup);

  }, [assembly]);

  const createAssemblyVisualization = (assembly: AssemblyResult): THREE.Group => {
    const group = new THREE.Group();

    try {
      // Create Part 1
      if (assembly.part1) {
        const part1Mesh = createPartMesh(assembly.part1, new THREE.Color(0x4a90e2));
        part1Mesh.userData.partName = "Part 1";
        group.add(part1Mesh);
      }

      // Create Part 2
      if (assembly.part2) {
        const part2Mesh = createPartMesh(assembly.part2, new THREE.Color(0x7ed321));
        part2Mesh.userData.partName = "Part 2";
        group.add(part2Mesh);
      }

      // Create Connector (if assembly is completed)
      if (assembly.status === 'completed' && assembly.connector) {
        const connectorMesh = createConnectorMesh(assembly);
        connectorMesh.userData.partName = "Connector";
        group.add(connectorMesh);
      }

      // Add constraint visualization
      if (assembly.parsedConstraints && assembly.parsedConstraints.length > 0) {
        const constraintVisualization = createConstraintVisualization(assembly.parsedConstraints);
        group.add(constraintVisualization);
      }

    } catch (error) {
      console.error('Error creating assembly visualization:', error);
    }

    return group;
  };

  const createPartMesh = (part: any, color: THREE.Color): THREE.Group => {
    const partGroup = new THREE.Group();
    
    if (part.geometry) {
      const geometry = part.geometry;
      const center = geometry.center || [0, 0, 0];
      const bbox = geometry.bounding_box;
      
      if (bbox && bbox.min && bbox.max) {
        const size = [
          bbox.max[0] - bbox.min[0],
          bbox.max[1] - bbox.min[1],
          bbox.max[2] - bbox.min[2]
        ];
        
        // Create box geometry
        const boxGeometry = new THREE.BoxGeometry(size[0], size[1], size[2]);
        const material = new THREE.MeshLambertMaterial({ 
          color: color,
          transparent: true,
          opacity: 0.8
        });
        
        const mesh = new THREE.Mesh(boxGeometry, material);
        mesh.position.set(center[0], center[1], center[2]);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        
        // Add wireframe
        const wireframeGeometry = new THREE.EdgesGeometry(boxGeometry);
        const wireframeMaterial = new THREE.LineBasicMaterial({ color: 0x000000 });
        const wireframe = new THREE.LineSegments(wireframeGeometry, wireframeMaterial);
        wireframe.position.copy(mesh.position);
        
        partGroup.add(mesh);
        partGroup.add(wireframe);
      }
    }
    
    return partGroup;
  };

  const createConnectorMesh = (assembly: AssemblyResult): THREE.Group => {
    const connectorGroup = new THREE.Group();
    
    // Get part positions to determine connector placement
    const part1Center = assembly.part1?.geometry?.center || [0, 0, 0];
    const part2Center = assembly.part2?.geometry?.center || [0, 0, 0];
    
    // Calculate connector position and size based on distance constraint
    const distanceConstraint = assembly.parsedConstraints?.find(c => c.type === 'distance');
    const distance = distanceConstraint?.value || 50;
    
    // Create connector based on distance
    let connectorGeometry: THREE.BufferGeometry | null = null;
    let connectorMaterial: THREE.Material | null = null;
    
    if (distance < 20) {
      // Small direct mount connector
      connectorGeometry = new THREE.BoxGeometry(distance, Math.min(15, distance * 0.8), Math.min(10, distance * 0.5));
      connectorMaterial = new THREE.MeshLambertMaterial({ color: 0xff9500, opacity: 0.9, transparent: true });
    } else if (distance < 50) {
      // L-bracket connector
      const thickness = 5;
      const bracket = new THREE.Group();
      
      // Horizontal part
      const horzGeom = new THREE.BoxGeometry(distance, thickness, 20);
      const horzMesh = new THREE.Mesh(horzGeom, new THREE.MeshLambertMaterial({ color: 0xff9500, opacity: 0.9, transparent: true }));
      horzMesh.position.set(0, -10, 0);
      bracket.add(horzMesh);
      
      // Vertical part
      const vertGeom = new THREE.BoxGeometry(thickness, 20, 20);
      const vertMesh = new THREE.Mesh(vertGeom, new THREE.MeshLambertMaterial({ color: 0xff9500, opacity: 0.9, transparent: true }));
      vertMesh.position.set(-distance/2, 0, 0);
      bracket.add(vertMesh);
      
      connectorGroup.add(bracket);
    } else {
      // Spacer block or beam
      connectorGeometry = new THREE.BoxGeometry(distance, Math.max(25, distance * 0.3), Math.max(20, distance * 0.25));
      connectorMaterial = new THREE.MeshLambertMaterial({ color: 0xff9500, opacity: 0.9, transparent: true });
    }
    
    if (connectorGeometry && connectorMaterial) {
      const connectorMesh = new THREE.Mesh(connectorGeometry, connectorMaterial);
      
      // Position connector between parts
      const centerPosition = [
        (part1Center[0] + part2Center[0]) / 2,
        (part1Center[1] + part2Center[1]) / 2,
        (part1Center[2] + part2Center[2]) / 2
      ];
      
      connectorMesh.position.set(centerPosition[0], centerPosition[1], centerPosition[2]);
      connectorMesh.castShadow = true;
      connectorMesh.receiveShadow = true;
      
      connectorGroup.add(connectorMesh);
    }
    
    return connectorGroup;
  };

  const createConstraintVisualization = (constraints: any[]): THREE.Group => {
    const constraintGroup = new THREE.Group();
    
    constraints.forEach((constraint, index) => {
      if (constraint.type === 'distance') {
        // Create distance visualization line
        const points = [];
        points.push(new THREE.Vector3(-constraint.value/2, 0, 30 + index * 5));
        points.push(new THREE.Vector3(constraint.value/2, 0, 30 + index * 5));
        
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({ color: 0xff0000, linewidth: 3 });
        const line = new THREE.Line(geometry, material);
        
        constraintGroup.add(line);
      }
    });
    
    return constraintGroup;
  };

  const getAssemblyStatus = () => {
    switch (assembly.status) {
      case 'processing':
        return { color: '#ff9800', text: '🔄 Processing...', icon: '⚙️' };
      case 'completed':
        return { color: '#4caf50', text: '✅ Assembly Complete', icon: '✨' };
      case 'failed':
        return { color: '#f44336', text: '❌ Assembly Failed', icon: '⚠️' };
      default:
        return { color: '#666', text: 'Unknown Status', icon: '?' };
    }
  };

  const status = getAssemblyStatus();

  return (
    <div style={{ position: 'relative', border: '2px solid #ddd', borderRadius: '8px', overflow: 'hidden' }}>
      <div style={{
        position: 'absolute',
        top: '8px',
        left: '8px',
        background: 'rgba(255, 255, 255, 0.95)',
        padding: '8px 12px',
        borderRadius: '6px',
        fontSize: '14px',
        fontWeight: 'bold',
        color: status.color,
        zIndex: 10,
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        {status.icon} {status.text}
      </div>
      
      {assembly.status === 'completed' && assembly.processingTime && (
        <div style={{
          position: 'absolute',
          top: '8px',
          right: '8px',
          background: 'rgba(255, 255, 255, 0.95)',
          padding: '4px 8px',
          borderRadius: '4px',
          fontSize: '12px',
          color: '#666',
          zIndex: 10
        }}>
          ⏱️ {assembly.processingTime}s
        </div>
      )}
      
      <div ref={mountRef} />
      
      {assembly.status === 'completed' && assembly.parsedConstraints && (
        <div style={{
          position: 'absolute',
          bottom: '8px',
          left: '8px',
          background: 'rgba(255, 255, 255, 0.95)',
          padding: '8px',
          borderRadius: '4px',
          fontSize: '12px',
          maxWidth: '200px',
          zIndex: 10
        }}>
          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>Constraints:</div>
          {assembly.parsedConstraints.map((constraint, index) => (
            <div key={index}>
              {constraint.type}: {constraint.value} {constraint.unit}
            </div>
          ))}
        </div>
      )}
      
      <div style={{
        position: 'absolute',
        bottom: '8px',
        right: '8px',
        color: '#999',
        fontSize: '10px',
        zIndex: 10
      }}>
        Mouse: Rotate | Scroll: Zoom
      </div>
    </div>
  );
};