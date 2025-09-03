import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';
import { UploadedFile } from '../types/assembly';

interface StepViewerProps {
  file: UploadedFile | null;
  width?: number;
  height?: number;
}

export const StepViewer: React.FC<StepViewerProps> = ({ 
  file, 
  width = 300, 
  height = 200 
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);

  useEffect(() => {
    if (!mountRef.current) return;
    
    const mountElement = mountRef.current;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(50, 50, 50);
    camera.lookAt(0, 0, 0);

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    rendererRef.current = renderer;
    mountElement.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
    directionalLight.position.set(50, 50, 25);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    // Grid
    const gridHelper = new THREE.GridHelper(100, 10);
    scene.add(gridHelper);

    // Controls (basic orbit controls simulation)
    let mouseDown = false;
    let mouseX = 0;
    let mouseY = 0;

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

      // Rotate camera around origin
      const spherical = new THREE.Spherical();
      spherical.setFromVector3(camera.position);
      spherical.theta -= deltaX * 0.01;
      spherical.phi += deltaY * 0.01;
      spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));

      camera.position.setFromSpherical(spherical);
      camera.lookAt(0, 0, 0);

      mouseX = event.clientX;
      mouseY = event.clientY;
    };

    const canvas = renderer.domElement;
    canvas.addEventListener('mousedown', onMouseDown);
    canvas.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('mousemove', onMouseMove);

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      canvas.removeEventListener('mousedown', onMouseDown);
      canvas.removeEventListener('mouseup', onMouseUp);
      canvas.removeEventListener('mousemove', onMouseMove);
      if (mountElement && renderer.domElement) {
        mountElement.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [width, height]);

  useEffect(() => {
    if (!file || !sceneRef.current) return;

    // Clear previous geometry
    const objectsToRemove = sceneRef.current.children.filter(
      child => child.userData.isCADPart
    );
    objectsToRemove.forEach(obj => sceneRef.current!.remove(obj));

    // Create mock geometry based on file name/size for now
    // In production, this would load the actual STEP file
    const mockGeometry = createMockGeometry(file);
    mockGeometry.userData.isCADPart = true;
    sceneRef.current.add(mockGeometry);

  }, [file]);

  const createMockGeometry = (file: UploadedFile): THREE.Object3D => {
    const group = new THREE.Group();
    
    // Create a simple box to represent the STEP part
    const size = Math.min(30, Math.max(10, file.size / 1000)); // Size based on file size
    const geometry = new THREE.BoxGeometry(size, size * 0.6, size * 0.4);
    
    const material = new THREE.MeshLambertMaterial({ 
      color: new THREE.Color().setHSL(Math.random(), 0.7, 0.6),
      transparent: true,
      opacity: 0.8
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    
    // Add wireframe
    const wireframeGeometry = new THREE.EdgesGeometry(geometry);
    const wireframeMaterial = new THREE.LineBasicMaterial({ color: 0x000000 });
    const wireframe = new THREE.LineSegments(wireframeGeometry, wireframeMaterial);
    
    group.add(mesh);
    group.add(wireframe);
    
    return group;
  };

  return (
    <div style={{ position: 'relative' }}>
      <div ref={mountRef} style={{ border: '1px solid #ddd', borderRadius: '4px' }} />
      {file && (
        <div style={{
          position: 'absolute',
          top: '8px',
          left: '8px',
          background: 'rgba(255, 255, 255, 0.9)',
          padding: '4px 8px',
          borderRadius: '4px',
          fontSize: '12px',
          color: '#666'
        }}>
          {file.name}
        </div>
      )}
      {!file && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: '#999',
          fontSize: '14px'
        }}>
          No file uploaded
        </div>
      )}
    </div>
  );
};