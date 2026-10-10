export const rules = [
  { number: '01', category: '书写', title: '姓名，是开始。', text: '在原作设定中，名字被写进笔记的人会死亡。这里的名字指向具体的人，而非一个称呼。', detail: '笔记的核心条件，是姓名与对象之间的对应。', tag: 'NAME' },
  { number: '02', category: '书写', title: '记住那张面容。', text: '写下名字时，书写者必须在心中想着对方的样貌。因此，同名的人不会一同受到影响。', detail: '姓名与面容共同确定对象。', tag: 'FACE' },
  { number: '03', category: '时间', title: '四十秒的空白。', text: '写完名字后，有四十秒可以写明死因。没有在这段时间内注明死因，默认结果是心脏麻痹。', detail: '计时从写下姓名之后开始。', tag: '40 SECONDS' },
  { number: '04', category: '时间', title: '六分四十秒。', text: '注明死因后，还有六分四十秒可以补充具体情况。书写的顺序与时间，都是规则的一部分。', detail: '这一时限用于进一步描述死亡的具体情况。', tag: '6 MIN 40 SEC' },
  { number: '05', category: '限制', title: '想象也有边界。', text: '指定的情况必须在现实条件下能够发生。无法实现的条件不会照写下的内容执行，结果可能回到默认死因。', detail: '原作对无法实现的死因、条件和牵连其他人的情况另有细则。', tag: 'LIMITS' },
  { number: '06', category: '死神', title: '看见另一侧。', text: '触碰死亡笔记的人，可以看见并听见与这本笔记相联系的死神，即使自己并不是持有者。', detail: '接触笔记，让原本看不见的存在显现。', tag: 'TOUCH' },
  { number: '07', category: '死神', title: '记忆随所有权离去。', text: '放弃死亡笔记的所有权，会失去与笔记有关的记忆。多本笔记的持有关系，在原作中另有说明。', detail: '这一设定与持有、接触和重新取得所有权有关。', tag: 'MEMORY' },
  { number: '08', category: '死神', title: '眼睛的交换。', text: '持有者可以与死神交易，用剩余寿命的一半，换取看见他人姓名和寿命的死神之眼。', detail: '交易的代价是持有者自己的剩余寿命。', tag: 'SHINIGAMI EYES' },
] as const

export const ruleFilters = ['全部', '书写', '时间', '限制', '死神'] as const
