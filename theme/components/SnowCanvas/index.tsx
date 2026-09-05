import { useEffect, useRef } from 'react';

type Particle = {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  drift: number;
  resting: number;
};

const vertexShader = `attribute vec2 a_position; attribute float a_size; uniform vec2 u_resolution; void main(){ vec2 p=a_position/u_resolution*2.0-1.0; gl_Position=vec4(p*vec2(1.0,-1.0),0.0,1.0); gl_PointSize=a_size; }`;
const snowFragment = `precision mediump float; void main(){ vec2 p=gl_PointCoord-.5; float a=smoothstep(.5,.18,length(p)); gl_FragColor=vec4(1.0,1.0,1.0,a*.82); }`;
const backgroundFragment = `precision mediump float; uniform vec2 u_resolution; uniform float u_dark; void main(){ vec2 uv=gl_FragCoord.xy/u_resolution; vec3 top=mix(vec3(.67,.86,.97),vec3(.07,.10,.16),u_dark); vec3 bottom=mix(vec3(.96,.97,.99),vec3(.055,.07,.11),u_dark); gl_FragColor=vec4(mix(top,bottom,smoothstep(0.,1.,uv.y)),1.0); }`;

function compile(gl: WebGLRenderingContext, type: number, source: string) {
  const shader = gl.createShader(type);
  if (!shader) throw new Error('Unable to create shader');
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  return shader;
}

export function SnowCanvas() {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const gl = canvas.getContext('webgl', { alpha: true, antialias: true });
    if (!gl) return;
    const dark = document.documentElement.classList.contains('dark');
    const makeProgram = (fragment: string) => {
      const p = gl.createProgram();
      if (!p) throw new Error('Unable to create program');
      gl.attachShader(p, compile(gl, gl.VERTEX_SHADER, vertexShader));
      gl.attachShader(p, compile(gl, gl.FRAGMENT_SHADER, fragment));
      gl.linkProgram(p);
      return p;
    };
    const snow = makeProgram(snowFragment);
    const bg = makeProgram(backgroundFragment);
    const pos = gl.createBuffer();
    const sizes = gl.createBuffer();
    const particles: Particle[] = [];
    const imageShell = canvas.parentElement?.querySelector<HTMLElement>(
      '.snow-hero__image-shell',
    );
    const actionButtons = canvas.parentElement?.querySelectorAll<HTMLElement>(
      '.snow-hero__actions .snow-button',
    );
    let width = 0;
    let height = 0;
    let dpr = 1;
    let barrier = { x: 0, y: 0, r: 0, active: false };
    let frame = 0;
    let last = performance.now();
    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      dpr = Math.min(devicePixelRatio || 1, 2);
      width = rect.width;
      height = rect.height;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      gl.viewport(0, 0, canvas.width, canvas.height);
      while (
        particles.length < Math.max(90, Math.floor((width * height) / 9000))
      )
        particles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.25,
          vy: 0.35 + Math.random() * 0.8,
          size: 1.5 + Math.random() * 3,
          drift: Math.random() * 6.28,
          resting: 0,
        });
    };
    const move = (e: MouseEvent) => {
      const r = canvas.getBoundingClientRect();
      barrier = {
        x: e.clientX - r.left,
        y: e.clientY - r.top,
        r: Math.max(48, Math.min(86, width * 0.075)),
        active: true,
      };
    };
    const leave = () => {
      barrier.active = false;
    };
    const render = (now: number) => {
      const dt = Math.min((now - last) / 16.67, 2);
      last = now;
      resize();
      // biome-ignore lint/correctness/useHookAtTopLevel: WebGL API method is named useProgram.
      gl.useProgram(bg);
      gl.uniform2f(
        gl.getUniformLocation(bg, 'u_resolution'),
        canvas.width,
        canvas.height,
      );
      gl.uniform1f(gl.getUniformLocation(bg, 'u_dark'), dark ? 1 : 0);
      gl.drawArrays(gl.TRIANGLES, 0, 0);
      const points: number[] = [];
      const sizesData: number[] = [];
      particles.forEach((p) => {
        p.vx += Math.sin(now * 0.0007 + p.drift) * 0.006 * dt;
        p.vx *= 0.995;
        p.vy = Math.min(p.vy + 0.006 * dt, 1.8);
        if (p.resting > 0) p.resting += dt;
        p.x += p.vx * dt;
        p.y += p.vy * dt;
        if (p.y > height + 8) {
          p.y = -8;
          p.x = Math.random() * width;
          p.vy = 0.35 + Math.random() * 0.8;
          p.resting = 0;
        }
        if (p.x < -8) p.x = width + 8;
        if (p.x > width + 8) p.x = -8;
        if (imageShell && p.vy > 0) {
          const imageRect = imageShell.getBoundingClientRect();
          const canvasRect = canvas.getBoundingClientRect();
          const left = imageRect.left - canvasRect.left;
          const right = imageRect.right - canvasRect.left;
          const top = imageRect.top - canvasRect.top;
          const bottom = imageRect.bottom - canvasRect.top;
          if (p.x >= left && p.x <= right && p.y >= top - 3 && p.y <= top + 8) {
            p.y = top - 3;
            p.vy = 0;
            p.resting = p.resting || 1;
            p.vx = 0;
          }
        }
        actionButtons?.forEach((button) => {
          const buttonRect = button.getBoundingClientRect();
          const canvasRect = canvas.getBoundingClientRect();
          const left = buttonRect.left - canvasRect.left;
          const right = buttonRect.right - canvasRect.left;
          const top = buttonRect.top - canvasRect.top;
          const bottom = buttonRect.bottom - canvasRect.top;
          if (p.x >= left && p.x <= right && p.y >= top - 3 && p.y <= top + 8) {
            p.y = top - 3;
            // Buttons collect snow instead of bouncing it between adjacent surfaces.
            p.vy = 0;
            p.vx *= 0.82;
            p.resting = p.resting || 1;
            p.vx = Math.max(-0.8, Math.min(0.8, p.vx));
          }
        });
        if (barrier.active) {
          const dx = p.x - barrier.x,
            dy = p.y - barrier.y,
            dist = Math.hypot(dx, dy);
          if (dist < barrier.r + 2) {
            const nx = dx / (dist || 1),
              ny = dy / (dist || 1);
            p.x = barrier.x + nx * (barrier.r + 2);
            p.y = barrier.y + ny * (barrier.r + 2);
            const dot = p.vx * nx + p.vy * ny;
            if (dot < 0) {
              p.vx -= 1.75 * dot * nx;
              p.vy -= 1.75 * dot * ny;
            }
            p.vx += -ny * 0.004;
            p.vx = Math.max(-0.9, Math.min(0.9, p.vx));
          }
        }
        if (p.resting > 360) {
          p.y = -8;
          p.x = Math.random() * width;
          p.vx = (Math.random() - 0.5) * 0.25;
          p.vy = 0.35 + Math.random() * 0.8;
          p.resting = 0;
        }
        points.push(p.x * dpr, p.y * dpr);
        sizesData.push(p.size * dpr);
      });
      // biome-ignore lint/correctness/useHookAtTopLevel: WebGL API method is named useProgram.
      gl.useProgram(snow);
      gl.uniform2f(
        gl.getUniformLocation(snow, 'u_resolution'),
        canvas.width,
        canvas.height,
      );
      gl.bindBuffer(gl.ARRAY_BUFFER, pos);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(points), gl.DYNAMIC_DRAW);
      const a = gl.getAttribLocation(snow, 'a_position');
      gl.enableVertexAttribArray(a);
      gl.vertexAttribPointer(a, 2, gl.FLOAT, false, 0, 0);
      gl.bindBuffer(gl.ARRAY_BUFFER, sizes);
      gl.bufferData(
        gl.ARRAY_BUFFER,
        new Float32Array(sizesData),
        gl.DYNAMIC_DRAW,
      );
      const s = gl.getAttribLocation(snow, 'a_size');
      gl.enableVertexAttribArray(s);
      gl.vertexAttribPointer(s, 1, gl.FLOAT, false, 0, 0);
      gl.drawArrays(gl.POINTS, 0, particles.length);
      frame = requestAnimationFrame(render);
    };
    canvas.addEventListener('mousemove', move);
    canvas.addEventListener('mouseleave', leave);
    window.addEventListener('resize', resize);
    resize();
    frame = requestAnimationFrame(render);
    return () => {
      cancelAnimationFrame(frame);
      canvas.removeEventListener('mousemove', move);
      canvas.removeEventListener('mouseleave', leave);
      window.removeEventListener('resize', resize);
    };
  }, []);
  return <canvas ref={ref} className="snow-canvas" />;
}
