
/** Prep data */
const mode = 'gen'
const cond = ''
const taskIds = prepConfigs(cond)


let aliceLearn = fmtConfig(taskIds['learnA'].map(id => config.filter(c => c['trial_id']==id)[0]), 'alice', 'learn')
let aliceGen = fmtConfig(shuffleArray(config.filter(c => taskIds['genA'].indexOf(c.trial_id) > -1)), 'alice', 'gen')

let bobLearn = fmtConfig(taskIds['learnB'].map(id => config.filter(c => c['trial_id']==id)[0]), 'bob', 'learn')
bobLearn.map(bl => bl.trial = bl.trial + aliceLearn.length)
let bobGen = fmtConfig(shuffleArray(config.filter(c => taskIds['genB'].indexOf(c.trial_id) > -1)), 'bob', 'gen')
bobGen.map(bg => bg.trial = bg.trial + aliceGen.length)

let sampleBase = document.getElementById('samples')
let aliceSummaryDiv = createCustomElement('div', 'summary-div', 'alice-summary-div');
let bobSummaryDiv = createCustomElement('div', 'summary-div', 'bob-summary-div');


if (mode==='gen') {
  let genConfigs = aliceGen
  genConfigs = genConfigs.sort((a, b) => parseInt(a.id.slice(1,)) - parseInt(b.id.slice(1,)))
  genConfigs.map(gc => gc.result = gc.recipient)

  console.log(genConfigs)
  let midPoint = Math.ceil(aliceGen.length/2)
  for(let i = 0; i < midPoint; i++ ) {
    aliceSummaryDiv.append(createSum(aliceGen[i], 'alice-sum'))
  }
  for(let i = midPoint; i < aliceGen.length; i++ ) {
    bobSummaryDiv.append(createSum(aliceGen[i], 'bob-sum'))
  }

} else {
  for(let i = 0; i < aliceLearn.length; i++ ) {
    aliceSummaryDiv.append(createSum(aliceLearn[i], 'alice-sum'))
  }
  for(let i = 0; i < bobLearn.length; i++ ) {
    bobSummaryDiv.append(createSum(bobLearn[i], 'bob-sum'))
  }
}



sampleBase.append(aliceSummaryDiv);
sampleBase.append(bobSummaryDiv);
