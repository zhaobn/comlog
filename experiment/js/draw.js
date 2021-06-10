
let baseDiv = document.getElementById('test')

let holderDiv = createCustomElement('svg', 'stone-svg', 'test-holder')
holderDiv.innerHTML = `
<circle cx="40" cy="40" r="30" stroke="black" stroke-width="1" fill="white" />
<line x1="${80-10-9}" y1="${40-30+9}" x2="${40-30+9}" y2="${80-10-9}" style="stroke:red;stroke-width:6" />
`
let holderDiv2 = createCustomElement('svg', 'stone-svg', 'test-holder')
holderDiv2.innerHTML = `
<circle cx="40" cy="40" r="30" stroke="black" stroke-width="1" fill="white" />
<line x1="${40+12.34}" y1="${40-12.34-15}" x2="${40-12.34-15}" y2="${40+12.34}" style="stroke:red;stroke-width:6" />
<line x1="${40+12.34+15}" y1="${40-12.34}" x2="${40-12.34}" y2="${40+12.34+15}" style="stroke:red;stroke-width:6" />
`

let holderDiv3 = createCustomElement('svg', 'stone-svg', 'test-holder')
holderDiv3.innerHTML = `
<circle cx="40" cy="40" r="30" stroke="black" stroke-width="1" fill="white" />
<line x1="${40+21.21}" y1="${40-21.21}" x2="${40-21.21}" y2="${40+21.21}" style="stroke:red;stroke-width:6" />
<line x1="${40+8.7}" y1="${40-8.7-20}" x2="${40-8.7-20}" y2="${40+8.7}" style="stroke:red;stroke-width:6" />
<line x1="${40+8.7+20}" y1="${40-8.7}" x2="${40-8.7}" y2="${40+8.7+20}" style="stroke:red;stroke-width:6" />
`

let holderDiv4 = createCustomElement('svg', 'stone-svg', 'test-holder')
holderDiv4.innerHTML = `
<circle cx="40" cy="40" r="30" stroke="black" stroke-width="1" fill="white" />
<line x1="${40+16.83}" y1="${40-16.83-8}" x2="${40-16.83-8}" y2="${40+16.83}" style="stroke:red;stroke-width:5" />
<line x1="${40+16.83+8}" y1="${40-16.83}" x2="${40-16.83}" y2="${40+16.83+8}" style="stroke:red;stroke-width:5" />
<line x1="${40+4.64}" y1="${40-4.64-25}" x2="${40-4.64-25}" y2="${40+4.64}" style="stroke:red;stroke-width:5" />
<line x1="${40+4.64+25}" y1="${40-4.64}" x2="${40-4.64}" y2="${40+4.64+25}" style="stroke:red;stroke-width:5" />
`

function getDelta(x, r = 30) {
  return (-x + Math.sqrt(2*(r**2)-x**2))/2
}

function createAgent(nStripes = 1, base = 40, r = 30) {
  let baseDiv = createCustomElement('svg', 'stone-svg', 'test-holder')
  let circleSvg = '<circle cx="40" cy="40" r="30" stroke="black" stroke-width="1" fill="white" />'
  let stripes = ''
  switch (nStripes) {
    case 1:
      stripes = `<line x1="${base+getDelta(0)}" y1="${base-getDelta(0)}" x2="${base-getDelta(0)}" y2="${base+getDelta(0)}" style="stroke:red;stroke-width:6" />`;
      break;
    case 2:
      stripes = `<line x1="${base+getDelta(15)}" y1="${base-getDelta(15)-15}" x2="${base-getDelta(15)-15}" y2="${base+getDelta(15)}" style="stroke:red;stroke-width:6" />` + '\n' +
      `<line x1="${base+getDelta(15)+15}" y1="${base-getDelta(15)}" x2="${base-getDelta(15)}" y2="${base+getDelta(15)+15}" style="stroke:red;stroke-width:6" />`
      break;
    case 3:
      stripes = `<line x1="${base+getDelta(15)}" y1="${base-getDelta(15)-15}" x2="${base-getDelta(15)-15}" y2="${base+getDelta(15)}" style="stroke:red;stroke-width:6" />` + '\n' +
      `<line x1="${base+getDelta(20)}" y1="${base-getDelta(20)-20}" x2="${base-getDelta(20)-20}" y2="${base+getDelta(20)}" style="stroke:red;stroke-width:6" />` + '\n' +
      `<line x1="${base+getDelta(20)+20}" y1="${base-getDelta(20)}" x2="${base-getDelta(20)}" y2="${base+getDelta(20)+20}" style="stroke:red;stroke-width:6" />`
    case 4:
      stripes = `<line x1="${base+getDelta(8)}" y1="${base-getDelta(8)-8}" x2="${base-getDelta(8)-8}" y2="${base+getDelta(8)}" style="stroke:red;stroke-width:6" />` + '\n' +
      `<line x1="${base+getDelta(8)+8}" y1="${base-getDelta(8)}" x2="${base-getDelta(8)}" y2="${base+getDelta(8)+8}" style="stroke:red;stroke-width:6" />` + '\n' +
      `<line x1="${base+getDelta(25)}" y1="${base-getDelta(25)-25}" x2="${base-getDelta(25)-25}" y2="${base+getDelta(25)}" style="stroke:red;stroke-width:6" />` + '\n' +
      `<line x1="${base+getDelta(25)+25}" y1="${base-getDelta(25)}" x2="${base-getDelta(25)}" y2="${base+getDelta(25)+25}" style="stroke:red;stroke-width:6" />`
      break;
  }
  baseDiv.innerHTML = circleSvg + stripes
  return(baseDiv)
}

baseDiv.append(createAgent(1))
baseDiv.append(createAgent(2))
baseDiv.append(createAgent(3))
baseDiv.append(createAgent(4))
