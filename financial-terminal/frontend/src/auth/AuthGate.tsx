import {createContext,useContext,useEffect,useState, type ReactNode, type FormEvent} from "react";
import type {User} from "../objects/auth";
import {GetCurrentUserMessage} from "../apis/accounts/GetCurrentUserMessage";
import {GetBootstrapInfoMessage} from "../apis/accounts/GetBootstrapInfoMessage";
import {LoginUserMessage} from "../apis/accounts/LoginUserMessage";
import {RegisterUserMessage} from "../apis/accounts/RegisterUserMessage";
import {LogoutUserMessage} from "../apis/sessions/LogoutUserMessage";
import {clearResearch} from "../stores/research";
const Identity=createContext<{user:User;refresh:()=>Promise<void>;logout:()=>Promise<void>}|null>(null);
export function useIdentity(){const value=useContext(Identity);if(!value)throw new Error("Authentication required");return value;}
export function AuthGate({children}:{children:ReactNode}){
 const [user,setUser]=useState<User|null>(null),[ready,setReady]=useState(false),[register,setRegister]=useState(false),[initialized,setInitialized]=useState(true),[error,setError]=useState(""),[busy,setBusy]=useState(false);
 function reset(){clearResearch();setUser(null);}
 async function refresh(){const result=await new GetCurrentUserMessage().send();setUser(result.user);}
 useEffect(()=>{let active=true;new GetCurrentUserMessage().send().then(r=>{if(active)setUser(r.user)}).catch(()=>{}).finally(()=>{if(active)setReady(true)});new GetBootstrapInfoMessage().send().then(r=>{if(active){setInitialized(r.initialized);setRegister(!r.initialized)}}).catch(()=>{});window.addEventListener("aperture:unauthorized",reset);return()=>{active=false;window.removeEventListener("aperture:unauthorized",reset)}},[]);
 async function submit(event:FormEvent<HTMLFormElement>){event.preventDefault();setBusy(true);setError("");const form=new FormData(event.currentTarget);try{const r=register?await new RegisterUserMessage(String(form.get("username")),String(form.get("password")),String(form.get("displayName"))).send():await new LoginUserMessage(String(form.get("username")),String(form.get("password"))).send();clearResearch();setUser(r.user);setInitialized(true)}catch(e){setError((e as Error).message)}finally{setBusy(false)}}
 if(!ready)return <div className="p-8 text-slate-400">正在验证会话…</div>;
 if(user)return <Identity.Provider value={{user,refresh,logout:async()=>{await new LogoutUserMessage().send();reset()}}}>{children}</Identity.Provider>;
 return <main className="min-h-screen bg-[#080d15] text-slate-200 flex items-center justify-center"><form onSubmit={submit} className="w-96 border border-slate-800 p-7 space-y-5"><div className="font-mono text-lg tracking-widest">APERTURE / ACCESS</div><h1 className="text-xl">{!initialized?"创建首个管理员账户":register?"创建研究账户":"登录金融终端"}</h1><p className="text-xs text-slate-500">{!initialized?"首个账户为管理员。后续账户默认为分析员。":"每个账户独立保存自选证券、分析报告与会话。"}</p><label className="block">用户名<input required name="username" autoComplete="username" pattern="[A-Za-z0-9_]{3,32}" className="block w-full mt-2" placeholder="3–32位字母、数字或下划线"/></label>{register&&<label className="block">显示名称<input required name="displayName" maxLength={64} className="block w-full mt-2"/></label>}<label className="block">密码<input required name="password" type="password" minLength={10} maxLength={128} autoComplete={register?"new-password":"current-password"} className="block w-full mt-2"/></label>{error&&<p role="alert" className="text-red-400 text-sm">{error}</p>}<button disabled={busy} type="submit" className="w-full bg-blue-600 p-2">{busy?"正在验证…":register?"创建账户":"登录"}</button>{initialized&&<button type="button" className="text-blue-400 text-sm" onClick={()=>{setRegister(!register);setError("")}}>{register?"已有账户，前往登录":"注册新账户"}</button>}</form></main>;
}
