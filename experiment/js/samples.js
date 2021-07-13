
/** Prep data */
const mode = 'dev'
const cond = 'comp_mult'
const taskIds = getConfigs(config, cond)

let aliceLearn = fmtConfig(config.filter(c => taskIds['learnA'].indexOf(c.trial_id) > -1), 'alice', 'learn')
let aliceGen = fmtConfig(shuffleArray(config.filter(c => taskIds['genA'].indexOf(c.trial_id) > -1)), 'alice', 'gen')

let bobLearn = fmtConfig(config.filter(c => taskIds['learnB'].indexOf(c.trial_id) > -1), 'bob', 'learn')
bobLearn.map(bl => bl.trial = bl.trial + aliceLearn.length)
let bobGen = fmtConfig(shuffleArray(config.filter(c => taskIds['genB'].indexOf(c.trial_id) > -1)), 'bob', 'gen')
bobGen.map(bg => bg.trial = bg.trial + aliceGen.length)

let sampleBase = document.getElementById('samples')

let aliceSummaryDiv = createCustomElement('div', 'summary-div', 'alice-summary-div');
let bobSummaryDiv = createCustomElement('div', 'summary-div', 'bob-summary-div');

for(let i = 0; i < aliceLearn.length; i++ ) {
  aliceSummaryDiv.append(createSum(aliceLearn[i], 'alice-sum'))
}

for(let i = 0; i < bobLearn.length; i++ ) {
  bobSummaryDiv.append(createSum(bobLearn[i], 'bob-sum'))
}

sampleBase.append(aliceSummaryDiv);
sampleBase.append(bobSummaryDiv);
