import { readFileSync } from 'node:fs';
import { resolve, sep } from 'node:path';
import { imageSize } from 'image-size';

type Node = {
  type: string;
  tagName?: string;
  properties?: Record<string, unknown>;
  children?: Node[];
};

/** Reserve intrinsic space at build time; keep the first content image eager. */
export function rehypeImages() {
  const publicRoot = resolve('docs/public');
  const sizes = new Map<string, { width: number; height: number }>();
  return (tree: Node) => {
    let imageIndex = 0;
    const walk = (node: Node) => {
      if (node.tagName === 'img' && typeof node.properties?.src === 'string') {
        const props = node.properties;
        const src = props.src as string;
        if (src.startsWith('/images/')) {
          const file = resolve(
            publicRoot,
            decodeURIComponent(src.split(/[?#]/)[0].slice(1)),
          );
          if (!file.startsWith(`${publicRoot}${sep}`))
            throw new Error(`Invalid image path: ${src}`);
          let size = sizes.get(file);
          if (!size) {
            size = imageSize(readFileSync(file));
            sizes.set(file, size);
          }
          props.width ??= size.width;
          props.height ??= size.height;
          props.loading ??= imageIndex === 0 ? 'eager' : 'lazy';
          props.decoding ??= 'async';
          imageIndex++;
        }
      }
      for (const child of node.children ?? []) walk(child);
    };
    walk(tree);
  };
}
