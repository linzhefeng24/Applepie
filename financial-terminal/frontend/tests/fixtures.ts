import {test as base,expect} from "@playwright/test";
export const test=base.extend({
 context:async({context},use)=>{
  const username="test_"+Date.now()+"_"+Math.random().toString(36).slice(2,7);
  const response=await context.request.post('/api/accounts/registeruser',{data:{username,password:"TestOnly_9vH8mK3x",displayName:"E2E Researcher"}});
  expect(response.ok(),await response.text()).toBeTruthy();
  await use(context);
 },
 request:async({context},use)=>{await use(context.request)}
});
export {expect};
