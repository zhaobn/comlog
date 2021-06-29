
function getDotPos(base=40, maxR=30) {
  let angle =  Math.floor(Math.random() * 90)
  let direction = Math.floor(Math.random() * 4)
  let sr = Math.floor(Math.random() * maxR)
  let sx = sr * Math.sin(angle)
  let sy = sr * Math.cos(angle)
  switch (direction) {
    case 0:
      x = base + sx
      y = base - sy
      break;
    case 1:
      x = base + sy
      y = base + sx
      break;
    case 2:
      x = base - sx
      y = base + sy
      break;
    case 3:
      x = base - sy
      y = base - sx
      break;
  }
  return({'x': x, 'y': y})
}

function isOverlapWith(pos1, pos2, delta = 20) {
  let distance = Math.sqrt((pos1.x-pos2.x)**2 + (pos1.y-pos2.y)**2)
  return (distance < delta)
}

function getDots (n, base=40, maxR=28) {
  let dotPos = []
  if (n<2) {
    dotPos.push(getDotPos(base, maxR))
  } else {
    while(dotPos.length < n) {
      let newPos = getDotPos(base, maxR)
      let overlap = 0
      for (let i=0; i<dotPos.length; i++) {
        let isOverlap = isOverlapWith(newPos, dotPos[i])
        overlap += isOverlap
      }
      if (overlap==0) {
        dotPos.push(newPos)
      }
    }
  }
  return dotPos
}

function addDots(n, base=40, maxR=26, color="black", size=4) {
  const dotPos = getDots(n, base, maxR)
  let dotHTML = []
  for (let i=0; i<dotPos.length; i++) {
    dotHTML.push(`<circle cx="${dotPos[i].x}" cy="${dotPos[i].y}" r="${size}" stroke="${color}" stroke-width="${size}"/>`)
  }
  return dotHTML.join('\n')
}

function createAgentStoneTest(id, agent = '1|1', color='red', base = 40, r = 25) {
  let nStripes = getStripes(agent)
  const getDelta = (x) => (-x + Math.sqrt(2*(r**2)-x**2))/2

  let agentDiv = createCustomElement("div", "agent-stone-div", `${id}-div`);
  let agentStoneSvg = createCustomElement('svg', 'stone-svg', id)
  let circleSvg = '<circle class="agent-stone" cx="40" cy="40" r="30" />'
  let stripes = ''

  switch (nStripes) {
    case 1:
      stripes = `<line class="agent-stone-stripe" x1="${base+getDelta(0)}" y1="${base-getDelta(0)}" x2="${base-getDelta(0)}" y2="${base+getDelta(0)}" stroke="${color}" />`;
      break;
    case 2:
      stripes = `<line class="agent-stone-stripe" x1="${base+getDelta(15)}" y1="${base-getDelta(15)-15}" x2="${base-getDelta(15)-15}" y2="${base+getDelta(15)}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(15)+15}" y1="${base-getDelta(15)}" x2="${base-getDelta(15)}" y2="${base+getDelta(15)+15}" stroke="${color}" />` + '\n'
      break;
    case 3:
      stripes = `<line class="agent-stone-stripe" x1="${base+getDelta(0)}" y1="${base-getDelta(0)}" x2="${base-getDelta(0)}" y2="${base+getDelta(0)}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(20)}" y1="${base-getDelta(20)-20}" x2="${base-getDelta(20)-20}" y2="${base+getDelta(20)}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(20)+20}" y1="${base-getDelta(20)}" x2="${base-getDelta(20)}" y2="${base+getDelta(20)+20}" stroke="${color}" />`
      break;
    case 4:
      stripes = `<line class="agent-stone-stripe" x1="${base+getDelta(8)}" y1="${base-getDelta(8)-8}" x2="${base-getDelta(8)-8}" y2="${base+getDelta(8)}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(8)+8}" y1="${base-getDelta(8)}" x2="${base-getDelta(8)}" y2="${base+getDelta(8)+8}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(25)}" y1="${base-getDelta(25)-25}" x2="${base-getDelta(25)-25}" y2="${base+getDelta(25)}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(25)+25}" y1="${base-getDelta(25)}" x2="${base-getDelta(25)}" y2="${base+getDelta(25)+25}" stroke="${color}" />`
      break;
  }
  agentStoneSvg.innerHTML = circleSvg + stripes + '\n' + addDots(4)
  agentDiv.append(agentStoneSvg)
  return agentDiv
}


let agentDiv = createCustomElement("div", "", `test-div`)
agentDiv.append(createAgentStoneTest(`test-agent`, '2|1'));

console.log(agentDiv)





document.body.append(agentDiv)
