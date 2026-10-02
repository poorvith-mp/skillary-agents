import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.dirname(fileURLToPath(import.meta.url));
const base = fs.readFileSync(path.join(root, 'pixel.svg'), 'utf8');
const states = {
  rest: '*{animation:none!important}.walk,.laptop{opacity:1;transform:none}.thought,.done{opacity:0}',
  walk: '.walk{animation:patrol 3s ease-in-out infinite alternate}.body{animation:step .4s ease-in-out infinite}.legA{animation:stride .4s infinite alternate}.legB{animation:stride .4s infinite alternate-reverse}.armA{animation:stride .4s infinite alternate-reverse}.armB{animation:stride .4s infinite alternate}.laptop,.thought,.done{animation:none;opacity:0}@keyframes patrol{from{transform:translateX(-100px)}to{transform:translateX(100px)}}@keyframes step{50%{transform:translateY(-6px)}}@keyframes stride{from{transform:rotate(-14deg)}to{transform:rotate(14deg)}}',
  think: '.walk,.body,.legA,.legB,.armA,.armB{animation:none;transform:none}.laptop,.done{animation:none;opacity:0}.thought{opacity:1;animation:idea 2s ease-in-out infinite}@keyframes idea{50%{transform:translateY(-5px);opacity:.6}}',
  work: '.walk,.body,.legA,.legB{animation:none;transform:none}.laptop{animation:none;opacity:1;transform:none}.thought,.done{animation:none;opacity:0}.armA{animation:type .45s infinite alternate}.armB{animation:type .45s infinite alternate-reverse}@keyframes type{from{transform:rotate(-9deg)}to{transform:rotate(7deg)}}',
  complete: '.walk,.legA,.legB,.armA,.armB{animation:none;transform:none}.body{animation:cheer 1.2s ease-in-out infinite}.laptop,.thought{animation:none;opacity:0}.done{animation:none;opacity:1}@keyframes cheer{40%{transform:translateY(-12px)}60%{transform:translateY(0)}}',
};
for (const [state, css] of Object.entries(states)) {
  const reduced = '@media(prefers-reduced-motion:reduce){*{animation:none!important}.walk,.body{transform:none}.laptop{opacity:1;transform:none}.thought,.done{opacity:0}}';
  fs.writeFileSync(path.join(root, `pixel-${state}.svg`), base.replace('</style>', css + reduced + '</style>').replace('Skillary pixel companion</title>', `Skillary pixel companion: ${state}</title>`));
}
console.log('Generated five pixel companion states.');

