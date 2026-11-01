import {test,expect} from "@playwright/test";
test("账户注册、资料、会话管理和退出后重新登录",async({page})=>{
 const username="browser_"+Date.now(),password="TestOnly_K3p8v7z2";
 await page.goto('/');await expect(page.getByRole('heading',{name:'登录金融终端'})).toBeVisible();
 await page.getByRole('button',{name:'注册新账户'}).click();
 await page.getByLabel('用户名').fill(username);await page.getByLabel('显示名称').fill('Browser Researcher');await page.getByLabel('密码',{exact:true}).fill(password);await page.getByRole('button',{name:'创建账户',exact:true}).click();
 await expect(page.getByRole('heading',{name:'证券筛选'})).toBeVisible();await page.goto('/account');
 await expect(page.getByRole('heading',{name:'账户与访问管理'})).toBeVisible();await page.getByLabel('显示名称').fill('Updated Researcher');await page.getByRole('button',{name:'保存资料'}).click();await expect(page.getByRole('status')).toContainText('已保存');
 await expect(page.getByRole('heading',{name:'用户权限'})).toHaveCount(0);await expect(page.getByRole('cell').filter({hasText:'当前'})).toHaveCount(1);
 await page.getByRole('button',{name:'退出登录',exact:true}).click();await expect(page.getByRole('heading',{name:'登录金融终端'})).toBeVisible();await expect(page.getByRole('heading',{name:'证券筛选'})).toHaveCount(0);
 await page.getByLabel('用户名').fill(username);await page.getByLabel('密码',{exact:true}).fill(password);await page.getByRole('button',{name:'登录',exact:true}).click();await expect(page.getByRole('heading',{name:'账户与访问管理'})).toBeVisible();await expect(page.getByLabel('显示名称')).toHaveValue('Updated Researcher');
});
