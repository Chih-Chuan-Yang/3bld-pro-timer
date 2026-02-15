# visualizer.py
import pycuber
import json
from utils import COLOR_PALETTE, PYCUBER_TO_WCA

def get_cube_state_colors(scramble_text):
    my_cube = pycuber.Cube()
    if scramble_text:
        clean_formula = " ".join([m for m in scramble_text.split() if 'w' not in m])
        try: my_cube(pycuber.Formula(clean_formula))
        except: pass

    face_colors = {}
    for face_name in ['U', 'D', 'F', 'B', 'L', 'R']:
        face_grid = my_cube.get_face(face_name)
        hex_list = []
        for row in face_grid:
            for square in row:
                wca_name = PYCUBER_TO_WCA.get(str(square), 'white')
                hex_list.append(COLOR_PALETTE[wca_name])
        face_colors[face_name] = hex_list
    return face_colors

def get_3d_html(scramble_text):
    cube_state = get_cube_state_colors(scramble_text)
    cube_state_json = json.dumps(cube_state)
    
    # 回傳完整的 HTML 字串
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; overflow: hidden; background: transparent; user-select: none; }}
            canvas {{ display: block; outline: none; }}
        </style>
    </head>
    <body>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        
        <script>
            const faceColors = {cube_state_json};
            const scene = new THREE.Scene();
            // 讓背景透明，融入 Streamlit 的 Dark Mode
            const camera = new THREE.PerspectiveCamera(40, window.innerWidth/window.innerHeight, 0.1, 100);
            camera.position.set(5, 5, 7); camera.lookAt(0,0,0);
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            document.body.appendChild(renderer.domElement);
            
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.autoRotate = true; // 增加一點動態感
            controls.autoRotateSpeed = 2.0;
            
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.8); scene.add(ambientLight);
            const dirLight = new THREE.DirectionalLight(0xffffff, 0.5); 
            dirLight.position.set(5, 10, 7); scene.add(dirLight);

            const group = new THREE.Group();
            scene.add(group);
            
            const geometry = new THREE.BoxGeometry(0.96, 0.96, 0.96);
            const edgesGeo = new THREE.EdgesGeometry(geometry);
            const edgeMat = new THREE.LineBasicMaterial({{ color: 0x000000, linewidth: 2 }});
            const coreMat = new THREE.MeshStandardMaterial({{ color: 0x111111 }});

            function getColor(face, idx) {{
                return new THREE.MeshStandardMaterial({{ color: faceColors[face][idx] }});
            }}

            for(let x=-1; x<=1; x++) {{
                for(let y=-1; y<=1; y++) {{
                    for(let z=-1; z<=1; z++) {{
                        const mats = Array(6).fill(coreMat);
                        if(x===1) {{ let col=(1-z); let row=(1-y); mats[0]=getColor('R', row*3+col); }}
                        if(x===-1) {{ let col=(z+1); let row=(1-y); mats[1]=getColor('L', row*3+col); }}
                        if(y===1) {{ let col=(x+1); let row=(z+1); mats[2]=getColor('U', row*3+col); }}
                        if(y===-1) {{ let col=(x+1); let row=(1-z); mats[3]=getColor('D', row*3+col); }}
                        if(z===1) {{ let col=(x+1); let row=(1-y); mats[4]=getColor('F', row*3+col); }}
                        if(z===-1) {{ let col=(1-x); let row=(1-y); mats[5]=getColor('B', row*3+col); }}

                        const cube = new THREE.Mesh(geometry, mats);
                        cube.position.set(x, y, z);
                        const edges = new THREE.LineSegments(edgesGeo, edgeMat);
                        cube.add(edges);
                        group.add(cube);
                    }}
                }}
            }}
            
            function animate() {{ requestAnimationFrame(animate); controls.update(); renderer.render(scene, camera); }}
            animate();
            window.addEventListener('resize', () => {{ camera.aspect=window.innerWidth/window.innerHeight; camera.updateProjectionMatrix(); renderer.setSize(window.innerWidth,window.innerHeight); }});
            
            // 滑鼠點擊時暫停自動旋轉
            window.addEventListener('mousedown', () => {{ controls.autoRotate = false; }});
        </script>
    </body>
    </html>
    """