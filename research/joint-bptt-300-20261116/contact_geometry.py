"""Native contact primals with analytic active-feature geometry derivatives.
Primal contact topology, distances, witnesses, frames and material parameters
come from the exact native collision stage. Smooth convex features are
implicitly differentiated through normal/witness stationarity; plane features
use their native primitive geometry. No finite-difference physics Jacobians.
At non-unique features the linearized KKT uses the minimum-norm solution.
"""
import jax
import jax.numpy as j
from mujoco.mjx._src import math


def features(kind,center,rotation,size,direction,point):
 local=rotation.T@(point-center)
 t=j.dot(point-center-size[0]*direction,rotation[:,2])
 return j.where(kind==3,j.array([t,0.,0.]),j.where((kind==5)|(kind==6),local,j.zeros(3)))


def shape_point(kind,center,rotation,size,normal,feature):
 q=rotation@j.diag(size**2)@rotation.T
 sphere=center+size[0]*normal
 ellipsoid=center+(q@normal)/j.sqrt(j.maximum(normal@q@normal,1e-30))
 capsule=sphere+feature[0]*rotation[:,2]
 cylinder=center+rotation@j.array([feature[1],feature[2],feature[0]])
 box=center+rotation@feature
 return j.where(kind==4,ellipsoid,j.where(kind==3,capsule,j.where(kind==5,cylinder,j.where(kind==6,box,sphere))))


def feature_equations(kind,rotation,size,normal,feature,reference,direction0):
 local=rotation.T@normal;initial=rotation.T@direction0
 tol=1e-6
 end=jax.lax.stop_gradient((j.abs(reference[0])>=size[1]-tol)|(j.abs(initial[2])>1e-5))
 target=jax.lax.stop_gradient(j.where(reference[0]>=0,1.,-1.))*size[1]
 axial=j.where(end,feature[0]-target,local[2])
 cap=j.array([axial,feature[1],feature[2]])
 radial_defined=jax.lax.stop_gradient(j.linalg.norm(initial[:2])>1e-5)
 norm=j.sqrt(j.maximum(j.sum(local[:2]**2),1e-30))
 radial=j.where(radial_defined,feature[1:]-size[0]*local[:2]/norm,local[:2])
 cyl=j.concatenate((j.array([axial]),radial))
 bound=jax.lax.stop_gradient((j.abs(reference)>=size-tol)|(j.abs(initial)>1e-5))
 box=j.where(bound,feature-j.where(reference>=0,1.,-1.)*size,local)
 return j.where(kind==3,cap,j.where(kind==5,cyl,j.where(kind==6,box,feature)))


def pair_contact(kind1,kind2,c1,c2,r1,r2,s1,s2,distance,point,frame,valid):
 """Differentiate a native convex witness without rerunning an approximate SDF."""
 normal0=frame[0]
 # Inactive/plane rows use a nonsingular dummy system and are masked out.
 use=valid&(kind1!=0)&(kind2!=0)
 n0=j.where(use,normal0,j.array([0.,0.,1.]))
 c1=j.where(use,c1,j.zeros(3));c2=j.where(use,c2,j.array([0.,0.,3.]))
 r1=j.where(use,r1,j.eye(3));r2=j.where(use,r2,j.eye(3));s1=j.where(use,s1,j.ones(3));s2=j.where(use,s2,j.ones(3));kind1=j.where(use,kind1,2);kind2=j.where(use,kind2,2)
 dist0=j.where(use,distance,1.);point0=j.where(use,point,j.array([0.,0.,1.5]))
 first=point0-.5*dist0*n0;second=point0+.5*dist0*n0
 f1=jax.lax.stop_gradient(features(kind1,c1,r1,s1,n0,first));f2=jax.lax.stop_gradient(features(kind2,c2,r2,s2,-n0,second))
 guess=jax.lax.stop_gradient(j.concatenate((n0,j.array([dist0]),f1,f2)))
 def residual(z):
  n=z[:3];distance=z[3];p1=shape_point(kind1,c1,r1,s1,n,z[4:7]);p2=shape_point(kind2,c2,r2,s2,-n,z[7:10])
  return j.concatenate((p2-p1-distance*n,j.array([.5*(j.dot(n,n)-1)]),feature_equations(kind1,r1,s1,n,z[4:7],f1,n0),feature_equations(kind2,r2,s2,-n,z[7:10],f2,-n0)))
 def tangent(operator,rhs):
  matrix=jax.vmap(operator)(j.eye(10,dtype=rhs.dtype)).T
  return j.linalg.pinv(matrix,rtol=1e-10)@rhs
 z=jax.lax.custom_root(residual,guess,lambda f,x:x,tangent)
 n=z[:3];p1=shape_point(kind1,c1,r1,s1,n,z[4:7]);p2=shape_point(kind2,c2,r2,s2,-n,z[7:10]);pos=.5*(p1+p2)
 basic=math.make_frame(n);align=jax.lax.stop_gradient(frame@math.make_frame(n0).T);newframe=align@basic
 return z[3],pos,newframe


def plane_contact(kind,cplane,rplane,center,rotation,size,distance,point,frame):
 n=rplane[:,2];surface0=point+.5*distance*frame[0]
 local=jax.lax.stop_gradient(rotation.T@(surface0-center))
 t=jax.lax.stop_gradient(j.dot(surface0-center+size[0]*n,rotation[:,2]))
 sphere=center-size[0]*n;capsule=sphere+t*rotation[:,2]
 q=rotation@j.diag(size**2)@rotation.T;ellipsoid=center-q@n/j.sqrt(j.maximum(n@q@n,1e-30))
 axis=rotation[:,2];rad=n-axis*j.dot(n,axis);norm=j.sqrt(j.maximum(j.dot(rad,rad),1e-30));axial=jax.lax.stop_gradient(j.dot(surface0-center,axis))
 radial=j.where(norm>1e-8,-size[0]*rad/norm,rotation[:,:2]@local[:2]);cylinder=center+axial*axis+radial
 box=center+rotation@local
 surface=j.where(kind==4,ellipsoid,j.where(kind==3,capsule,j.where(kind==5,cylinder,j.where(kind==6,box,sphere))))
 distance=j.dot(surface-cplane,n);pos=surface-.5*distance*n
 return distance,pos,frame


def attach(m,d,packed,geoms):
 """All native contact values remain exact; only their derivatives are supplied."""
 g1,g2=geoms[:,0],geoms[:,1];types=j.asarray(m.geom_type);kind1,kind2=types[g1],types[g2]
 dist=packed[:,0];pos=packed[:,1:4];frame=packed[:,4:13].reshape((-1,3,3));valid=dist<1e5
 c1,c2=d.geom_xpos[g1],d.geom_xpos[g2];r1,r2=d.geom_xmat[g1],d.geom_xmat[g2];s1,s2=m.geom_size[g1],m.geom_size[g2]
 pd,pp,pf=jax.vmap(pair_contact)(kind1,kind2,c1,c2,r1,r2,s1,s2,dist,pos,frame,valid)
 plane_dist,plane_pos,plane_frame=jax.vmap(plane_contact)(kind2,c1,r1,c2,r2,s2,dist,pos,frame)
 isplane=(kind1==0)&valid
 ad=j.where(isplane,plane_dist,pd);ap=j.where(isplane[:,None],plane_pos,pp);af=j.where(isplane[:,None,None],plane_frame,pf)
 # Native CCD convergence tolerances must not change the actual forward values.
 dist=dist+(ad-jax.lax.stop_gradient(ad))*valid
 pos=pos+(ap-jax.lax.stop_gradient(ap))*valid[:,None]
 frame=frame+(af-jax.lax.stop_gradient(af))*valid[:,None,None]
 contact=d.contact.replace(dist=dist,pos=pos,frame=frame,geom=geoms,geom1=g1,geom2=g2,includemargin=packed[:,27],friction=packed[:,13:18],solref=packed[:,18:20],solreffriction=packed[:,20:22],solimp=packed[:,22:27])
 return d.replace(contact=contact)
