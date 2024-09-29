import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

const RoverScene = ({ robotState }) => {
    const mountRef = useRef(null); // Ref to attach the Three.js canvas
    const roverRef = useRef(null); // Ref to store the rover model

    useEffect(() => {
        // Main scene setup
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);

        // Attach the renderer's canvas to the DOM
        if (mountRef.current) {
            mountRef.current.appendChild(renderer.domElement);
        }

        // Set up orbit controls for the camera
        const controls = new OrbitControls(camera, renderer.domElement);
        camera.position.set(0, 1, 5);

        // Add a light to the scene
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6); // Soft white light
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8); // Stronger directional light
        directionalLight.position.set(5, 10, 7.5);
        scene.add(directionalLight);

        // Load the rover model
        const loader = new GLTFLoader();
        loader.load('/models/therover.glb', (gltf) => {
            const rover = gltf.scene;
            roverRef.current = rover;
            rover.scale.set(0.2, 0.2, 0.2);
            rover.rotation.y -= Math.PI /4 ;

           

            scene.add(rover);

            // Traverse the model and adjust materials
            rover.traverse((child) => {
                if (child.isMesh) {
                    // Ensure the material is not transparent
                    child.material.transparent = false;
                    child.material.opacity = 1;
                    child.material.color.set(0xd3d3d3); // Light grey color
                }
            });
        }, undefined, (error) => {
            console.error('An error occurred while loading the model:', error);
        });

        const animate = () => {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        };

        animate(); // Start the animation

        // Handle window resizing
        const handleResize = () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        };
        window.addEventListener('resize', handleResize);

        // Cleanup function
        return () => {
            if (mountRef.current) {
                mountRef.current.removeChild(renderer.domElement);
            }
            renderer.dispose();
            window.removeEventListener('resize', handleResize);
        };
    }, []); // empty dependency array (this effect runs once on mount)

    return <div ref={mountRef} style={{ width: '100%', height: '100vh' }} />;
};

export default RoverScene;
