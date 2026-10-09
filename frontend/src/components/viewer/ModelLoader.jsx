import React, { useEffect } from 'react';
import { useGLTF, Center } from '@react-three/drei';

export function ModelLoader({ url }) {
  const { scene } = useGLTF(url);

  // Clean up geometry / materials when unmounted to prevent WebGL leaks
  useEffect(() => {
    return () => {
      scene?.traverse((child) => {
        if (child.isMesh) {
          child.geometry?.dispose();
          if (Array.isArray(child.material)) {
            child.material.forEach((mat) => mat.dispose());
          } else {
            child.material?.dispose();
          }
        }
      });
    };
  }, [scene]);

  return (
    <Center top>
      <primitive object={scene} scale={1.5} />
    </Center>
  );
}

export default ModelLoader;
