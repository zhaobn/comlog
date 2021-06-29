function getDotPos(n, base=40, maxR=30, color="black", size=3) {
  let dotPos = []
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
      `<line class="agent-stone-stripe" x1="${base+getDelta(15)+15}" y1="${base-getDelta(15)}" x2="${base-getDelta(15)}" y2="${base+getDelta(15)+15}" stroke="${color}" />` + '\n' +
      `<circle cx="50" cy="50" r="4" stroke="black" stroke-width="3"/>` + '\n' +
      `<circle cx="20" cy="30" r="4" stroke="black" stroke-width="3"/>`
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
  agentStoneSvg.innerHTML = circleSvg + stripes
  agentDiv.append(agentStoneSvg)
  return agentDiv
}


let agentDiv = createCustomElement("div", "", `test-div`)
agentDiv.append(createAgentStoneTest(`test-agent`, '2|1'));

console.log(agentDiv)





document.body.append(agentDiv)
