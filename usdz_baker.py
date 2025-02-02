from maya import cmds
from functools import partial
import json
import os
import shutil
import random
import string
import os
import re
import maya.mel as mel
from pxr import Usd

def export_usdz(fmin,fmax):

    #out_filename = "{0}_{1}_static.usdz".format(filename.split(".")[0],name)    

    #fmin = cmds.playbackOptions(q=True,min=True)
    #fmax = cmds.playbackOptions(q=True,max=True)
    #print fmax

    usdFilePath='/Users/hiroyukiokubo/WORK/Projects/PencilPot/maya/usdz/badge_open.usdz'
    #usdFilePath='test.usdz'
    cmds.file(usdFilePath, type="USD Export",options="defaultMeshScheme=catmullClark;mergeTransformAndShape=1;exportVisibility=1;exportColorSets=1;exportUVs=1;stripNamespaces=1;frameStride=1;frameSample=0;animation=0;startTime=1;parentScope=;eulerFilter=0;endTime=1;exportInstances=0", es=True,preserveReferences=True, force=True)   

#stripNamespaces=1" -typ "USD Export" -pr -es "/Users/hiroyukiokubo/WORK/Projects/PencilPot/maya/usdz/badge_open.usdz";

       
def export_anim_usdz(outfilepath,fmin,fmax):
    (_, major, minor) = Usd.GetVersion()
    creator = 'USD {}.{} Maya Plugin (Apple Internal a0)'.format(str(major), str(minor).zfill(2))
    print(creator)
    
    #filename = cmds.file(q=True,shn=True,sn=True)
    #filepath = os.path.dirname(cmds.file(q=True,sn=True))
    #objname = cmds.ls(sl=True)[0];
    #out_filename = "{0}_{1}_static.usdz".format(filename.split(".")[0],objname)
    #out_filename = "{0}_{1}_static.usdz".format(filename.split(".")[0],name)    
    #out_filename=outfilepath
    #SEPARATOR = ":::"
    #usdFilePath='{1}/{0}'.format(out_filename,filepath)
    #data = {'copyright': 'Copyright (c) 2021 Apple Inc. All rights reserved.','creator': creator, 'timeCodesPerSecond': str(mel.eval('float $fps = `currentTimeUnitToFPS`'))}
    #data = {'creator': creator, 'timeCodesPerSecond': str(mel.eval('float $fps = `currentTimeUnitToFPS`'))}
   
    #metadata_str = ''
    #for key, value in data.items():
    #    if metadata_str:
    #        metadata_str += SEPARATOR
    #    metadata_str += '{}={}'.format(key, value)

    #fmin = cmds.playbackOptions(q=True,min=True)
    #fmax = cmds.playbackOptions(q=True,max=True)
    #print fmax
    #usdFilePath='/Users/hiroyukiokubo/WORK/Projects/PencilPot/maya/usdz/badge_open.usdz'
    print("Output")
    print(outfilepath)
    cmds.mayaUSDExport(
        file=outfilepath,
        #chaser=['apl_metadata'],
        #chaserArgs=[
        #   ('apl_metadata', 'rootlayer', metadata_str)
        #],
        defaultMeshScheme='none',
        shadingMode='useRegistry',
        exportDisplayColor=True,
        exportRefsAsInstanceable=False,
        exportUVs=True,
        exportMaterialCollections=False,
        mergeTransformAndShape=True,
        exportSkin='auto',
        exportSkels='auto',
        frameRange=[fmin,fmax],
        frameStride=1,
        compatibility='appleArKit',
        sl=True
        )
    

def scrambleScene():
    #project = instance.data['rtExportProject']
    #scene_file = instance.data['rtExportScene']
    #cmds.workspace(project, openWorkspace=True)
    #cmds.file(scene_file, open=True, force=True)
    project = cmds.workspace( q=True, active=True )
    scene_file = cmds.file(q=True,sn=True)



    # rename xforms / geos
    rename_blacklist = ["persp", "top", "front", "side",
                        "tracking_node_placeholder"]

    all_xforms = cmds.ls(type="transform")
    for xform in all_xforms:
        if xform not in rename_blacklist:
            new_name = random_string()
            try:
                cmds.rename(xform, new_name)
                print("Transform node {0} "
                           "renamed to {1}".format(xform,
                                                   new_name))
            except:
                print("Failed to rename transform node {0}").format(xform)

    # rename shading nodes
    rename_shader_types = ["shadingEngine",
                           "file",
                           "place2dTexture",
                           "pxrUsdPreviewSurface"]
    rename_shader_blacklist = ["initialShadingGroup",
                               "initialParticleSE",
                               "lambert1"]

    all_shading_nodes = cmds.ls(type=rename_shader_types)
    for shading_node in all_shading_nodes:
        #print shading_node
        if shading_node not in rename_shader_blacklist:
            new_name = random_string()
            try: 
                cmds.rename(shading_node, new_name)
                print("Shading node {0} "
                           "renamed to {1}".format(shading_node,
                                                   new_name))
            except:
                print("Failed to rename Shading node {0}").format(xform)

    # Get all texture file nodes
    all_tex_nodes = cmds.ls(type="file")
    # collect texture path to texture file nodes dict
    path_to_node = {}
    for tex_node in all_tex_nodes:
        tex_path = cmds.getAttr(tex_node + ".fileTextureName")
        if tex_path in path_to_node.keys():
            path_to_node[tex_path].append(tex_node)
        else:
            path_to_node[tex_path] = [tex_node]

    # rename textures
    for tex_cur_path, tex_nodes in path_to_node.items():
        # prevent out-of-package renaming
        if project not in tex_cur_path:
            print("Texture file {0} is not in project!"
                           " Skipping ...".format(tex_cur_path))
            continue

        # skip texture if it does not exist
        if not os.path.exists(tex_cur_path):
            print("Texture file {0}"
                           " does not exist!".format(tex_cur_path))
            continue

        # make a new name for the texture
        tex_dir = os.path.dirname(tex_cur_path)
        tex_ext = os.path.splitext(tex_cur_path)[-1]
        new_name = random_string() + tex_ext
        tex_new_path = os.path.join(tex_dir, new_name)
        # rename texture
        shutil.copy(tex_cur_path, tex_new_path)
        print("texture file {0} "
                       "renamed to {1}".format(tex_cur_path,
                                               tex_new_path))
        # set new texture name each file node that uses it
        for tex_node in tex_nodes:
            cmds.setAttr(tex_node + ".fileTextureName",
                         tex_new_path, type="string")


        filename = cmds.file(q=True,shn=True,sn=True)
        filepath = os.path.dirname(cmds.file(q=True,sn=True))
        #out_filename = "{1}/{0}_scrambled.ma".format(filename.split(".")[0],filepath)
        out_filename = "{1}/{0}.ma".format(random_string(),filepath)
        
        # save scrambled file
        cmds.file( rename=out_filename )
        
        #cmds.file(save=Trw, type='mayaAscii')
        #Create Folder
        filepath = cmds.file(q=True, sn=True)
        
        #fparts=filepath.split('/')
        #fparts[len(fparts)-1]=fparts[len(fparts)-1]+'_added'
        #renamed_path='/'.join(fparts)
        #cmds.file( rename=renamed_path )
        
        #cmds.file(save=True, type="mayaAscii")

def random_string(leng=15):
    return ''.join(random.choice(string.ascii_letters) for i in range(leng))

def bake(grp):

    # bakes neon  attributes on all objects and then adds small value delta to first/last frames
    
    tx=grp_list[grp]['tx']
    ty=grp_list[grp]['ty']
    tz=grp_list[grp]['tz']

    rx=grp_list[grp]['rx']
    ry=grp_list[grp]['ry']
    rz=grp_list[grp]['rz']

    sx=grp_list[grp]['sx']
    sy=grp_list[grp]['sy']
    sz=grp_list[grp]['sz']
    
    set_array=[tx,ty,tz,rx,ry,rz,sx,sy,sz]
    ats=["tx","ty","tz","rx","ry","rz","sx","sy","sz"]
    for set,at in zip(set_array,ats):
        if set==0:
            ats.remove(at)
    #print ats
    # get min max animation range
    tmin = cmds.playbackOptions(q=True,min=True)
    tmax = cmds.playbackOptions(q=True,max=True)
    
    # bake transforms without simulation enabled (faster bake)
    
    obj_list=cmds.listRelatives(grp,c=True,ad=True,type='joint',s=False,ni=True)
    #obj_list = cmds.ls(sl=True)
    cmds.bakeResults(obj_list,
        simulation=True,
        time=(tmin,tmax),
        sampleBy=1,
        oversamplingRate=1,
        disableImplicitControl=True,
        preserveOutsideKeys=False,
        sparseAnimCurveBake=False,
        removeBakedAttributeFromLayer=False,
        bakeOnOverrideLayer=False,
        minimizeRotation=True,
        at=ats)
        
    sl = cmds.keyframe(obj_list,q=True,name=True)


    # find all animation curves and tweak small value deltas on first and last frame
    for each in sl:
        val = cmds.keyframe(each,q=True,time=(tmin,tmin),eval=True)[0]
        cmds.setKeyframe(each,time=tmin,value=val+.0001)
        val = cmds.keyframe(each,q=True,time=(tmax,tmax),eval=True)[0]
        cmds.setKeyframe(each,time=tmax,value=val+.0001)
        
    cmds.keyTangent(obj_list,e=True,itt='stepnext',ott='step')

def fresh_bind(grp):
    #print grp
    objs=cmds.listRelatives(grp,c=True,ad=True,type='mesh',s=False,ni=True)
    geoName=''
    for obj in objs:
        skin_cluster = cmds.listConnections(obj+".inMesh",type="skinCluster")
        if skin_cluster!=None:
            geoName=cmds.listRelatives(obj,p=True,typ='transform')[0]
    #print geoName
    if geoName!='':                
        bindposef=grp_list[grp]['bindposef']
        cmds.currentTime( bindposef, edit=True )
        #print bindposef
        
        #geoName = cmds.ls(sl=True)[0]
        skin_src = geoName+"_sourceSkin"
        skin_cluster = cmds.listConnections(geoName+".inMesh",type="skinCluster")
        jnts = cmds.skinCluster(skin_cluster,q=True, inf=True)
        root_jnt = jnts[0];

        
        jnt_fullpath = cmds.ls(jnts, l=True)[0].split('|')
        for i in jnt_fullpath :                
            if cmds.ls('|'.join(jnt_fullpath[:jnt_fullpath.index(i)+1]), type='joint') :
                root_jnt = i


        for ea in jnts:
            if (cmds.getAttr("{0}.ty".format(ea))+cmds.getAttr("{0}.ty".format(root_jnt)))< 0:
                cmds.setAttr("{0}.ty".format(ea),0.01-cmds.getAttr("{0}.ty".format(root_jnt)) )  
                          
        print ("Binding to root joint {0}".format(root_jnt))
        cmds.rename(geoName, skin_src)
        cmds.duplicate(skin_src, n=geoName)
        bind_jnts = cmds.skinCluster(skin_cluster,q=1,inf=True)

        
        trg_skin = skin_src.rsplit("_", 1)[0] + "_rebindSkinCluster"
        cmds.skinCluster(bind_jnts, geoName, n=trg_skin,sm=0, nw=1, mi=1, tsb=True)
        cmds.copySkinWeights(ss=skin_cluster[0], ds=trg_skin,nm=True,sa="closestPoint",ia="oneToOne")
        bind_pose = cmds.listConnections(trg_skin, s=True, t="dagPose")
        bind_pose.extend(cmds.listConnections(root_jnt, d=True, t="dagPose"))
        cmds.delete(bind_pose)
        cmds.select(cl=True)
        
        parent_node=cmds.listRelatives(root_jnt,p=True)
        cmds.parent(root_jnt,w=True)
        
        cmds.select(bind_jnts)
        cmds.dagPose(bp=True, s=True, selection=True, n=geoName + "_bindPose")
        cmds.delete(skin_src)
        
        cmds.parent(root_jnt,parent_node)


def add():
    sl=cmds.ls(sl=True)
    if len(sl)>0:
        cmds.textScrollList(src, e=True,a=sl)
        cmds.textScrollList(src, e=True,si=sl)
        set()
        
        asset_list=cmds.textScrollList(src, q=True, si=True)

        for asset in asset_list:
            cmds.textScrollList(src, e=True,di=asset)
        cmds.textScrollList(src, e=True,si=sl[0])

def rm():
    selectedItems = cmds.textScrollList (src , query = True, selectItem = True)

    for item in selectedItems:
        cmds.textScrollList(src,e=True,removeItem=item)
        grp_list.pop(item,None)


def clr():
    cmds.textScrollList(src,e=True,removeAll=True)
    
def setbake():
    trans=cmds.checkBoxGrp(trans_ins,q=True,v1=True)
    rot=cmds.checkBoxGrp(rot_ins,q=True,v1=True) 
    scale=cmds.checkBoxGrp(scale_ins,q=True,v1=True)
    
    if trans == 1:
        cmds.checkBoxGrp(trans_ins,e=True,v2=1)
        cmds.checkBoxGrp(trans_ins,e=True,v3=1)
        cmds.checkBoxGrp(trans_ins,e=True,v4=1)
    else:
        cmds.checkBoxGrp(trans_ins,e=True,v2=0)
        cmds.checkBoxGrp(trans_ins,e=True,v3=0)
        cmds.checkBoxGrp(trans_ins,e=True,v4=0)
        
    if rot == 1:
        cmds.checkBoxGrp(rot_ins,e=True,v2=1)
        cmds.checkBoxGrp(rot_ins,e=True,v3=1)
        cmds.checkBoxGrp(rot_ins,e=True,v4=1)
    else:
        cmds.checkBoxGrp(rot_ins,e=True,v2=0)
        cmds.checkBoxGrp(rot_ins,e=True,v3=0)
        cmds.checkBoxGrp(rot_ins,e=True,v4=0)
        
    if scale == 1:
        cmds.checkBoxGrp(scale_ins,e=True,v2=1)
        cmds.checkBoxGrp(scale_ins,e=True,v3=1)
        cmds.checkBoxGrp(scale_ins,e=True,v4=1)
    else:
        cmds.checkBoxGrp(scale_ins,e=True,v2=0)
        cmds.checkBoxGrp(scale_ins,e=True,v3=0)
        cmds.checkBoxGrp(scale_ins,e=True,v4=0)
        
    set()

def init():


    last_item=''
    objs=cmds.ls(v=True,tr=True,type='objectSet')
    #After Scrambling, we need to check name attribute to export proper asset.
    for obj in objs:
        atchk=cmds.attributeQuery( 'parms', node=obj,ex=True)
        type=cmds.nodeType(obj)
        if atchk and type=='objectSet':
            cmds.textScrollList(src, e=True,a=obj)
            last_item=obj
            
    cmds.textScrollList(src, e=True,si=last_item)
'''     
    srcgrpLists = cmds.textScrollList(src, q=True,ai=True)        
    if srcgrpLists !=None:
        for grp in srcgrpLists:
            atchk=cmds.attributeQuery( 'parms', node=grp,ex=True)
            if atchk == True:
                  str_parms=cmds.getAttr(grp+'.parms')
                  if len(str_parms) > 0:
                      #print "init:"+grp
                      parms = json.loads(str_parms)
                      grp_list.update(parms)
                      
                      cmds.intSliderGrp(start_ins,e=True,v=parms[grp]['sf'])
                      cmds.intSliderGrp(end_ins,e=True,v=parms[grp]['ef'])
                      cmds.intSliderGrp(fps_ins,e=True,v=parms[grp]['fps'])
                      
                      cmds.checkBoxGrp(trans_ins,e=True,v1=parms[grp]['trans'])
                      cmds.checkBoxGrp(trans_ins,e=True,v2=parms[grp]['tx'])
                      cmds.checkBoxGrp(trans_ins,e=True,v3=parms[grp]['ty'])
                      cmds.checkBoxGrp(trans_ins,e=True,v4=parms[grp]['tz'])
        
                      cmds.checkBoxGrp(rot_ins,e=True,v1=parms[grp]['rot'])
                      cmds.checkBoxGrp(rot_ins,e=True,v2=parms[grp]['rx'])
                      cmds.checkBoxGrp(rot_ins,e=True,v3=parms[grp]['ry'])
                      cmds.checkBoxGrp(rot_ins,e=True,v4=parms[grp]['rz'])
        
                      cmds.checkBoxGrp(scale_ins,e=True,v1=parms[grp]['scale'])
                      cmds.checkBoxGrp(scale_ins,e=True,v2=parms[grp]['sx'])
                      cmds.checkBoxGrp(scale_ins,e=True,v3=parms[grp]['sy'])
                      cmds.checkBoxGrp(scale_ins,e=True,v4=parms[grp]['sz'])
                                   
                      #cmds.checkBoxGrp(bp_ins,e=True,v1=parms[grp]['bindpose'])
                      #cmds.intSliderGrp(bindpose_frame_ins,e=True,en=parms[grp]['bindpose'])
                      #cmds.intSliderGrp(bindpose_frame_ins,e=True,v=parms[grp]['bindposef'])
    #print grp_list
'''
                                  
# Write Parms        
def set():
    srcgrpLists = cmds.textScrollList(src, q=True, si=True)
    startf=cmds.intSliderGrp(start_ins,q=True,v=True)
    endf=cmds.intSliderGrp(end_ins,q=True,v=True)
    fps=cmds.intSliderGrp(fps_ins,q=True,v=True)
    
    ts=cmds.checkBoxGrp(trans_ins,q=True,v1=True)
    tx=cmds.checkBoxGrp(trans_ins,q=True,v2=True)
    ty=cmds.checkBoxGrp(trans_ins,q=True,v3=True)
    tz=cmds.checkBoxGrp(trans_ins,q=True,v4=True)

    rot=cmds.checkBoxGrp(rot_ins,q=True,v1=True)
    rx=cmds.checkBoxGrp(rot_ins,q=True,v2=True)
    ry=cmds.checkBoxGrp(rot_ins,q=True,v3=True)
    rz=cmds.checkBoxGrp(rot_ins,q=True,v4=True)

    sc=cmds.checkBoxGrp(scale_ins,q=True,v1=True)
    sx=cmds.checkBoxGrp(scale_ins,q=True,v2=True)
    sy=cmds.checkBoxGrp(scale_ins,q=True,v3=True)
    sz=cmds.checkBoxGrp(scale_ins,q=True,v4=True)
 
    #bindpose=cmds.checkBoxGrp(bp_ins,q=True,v1=True)
    #cmds.intSliderGrp(bindpose_frame_ins,e=True,en=bindpose)
    #bindposef=cmds.intSliderGrp(bindpose_frame_ins,q=True,v=True)
 
    if srcgrpLists !=None:
        for asset in srcgrpLists:
            #parms={asset:{'sf':startf,'ef':endf,'fps':fps,'trans':ts,'tx':tx,'ty':ty,'tz':tz,'rot':rot,'rx':rx,'ry':ry,'rz':rz,'scale':sc,'sx':sx,'sy':sy,'sz':sz,'bindpose':bindpose,'bindposef':bindposef}}
            parms={asset:{'sf':startf,'ef':endf,'fps':fps,'trans':ts,'tx':tx,'ty':ty,'tz':tz,'rot':rot,'rx':rx,'ry':ry,'rz':rz,'scale':sc,'sx':sx,'sy':sy,'sz':sz}}
            grp_list.update(parms)

            atchk=cmds.attributeQuery( 'parms', node=asset,ex=True)
            if atchk == False:
                cmds.addAttr( asset, ln='parms', dt='string' )
            cmds.setAttr( asset+'.parms', json.dumps(parms), type='string' )

    #print grp_list
    
def drop():
    selectedItems = cmds.textScrollList (src , query = True, selectItem = True)
    for grp in selectedItems:
        str_parms=cmds.getAttr(grp+'.parms')
        parms = json.loads(str_parms)
        fps=parms[grp]['fps']
        fps_str=str(fps)+'fps'
        cmds.currentUnit(time=fps_str)
        #print fps_str

def debug_show(): 
    filepath = cmds.file(q=True, sn=True)
    fparts=filepath.split('/')
    name=fparts[len(fparts)-1]
   
    selectedItems = cmds.textScrollList (src , query = True, selectItem = True)
    dir=cmds.textField(outputDir , query = True,tx=True)
    #print(dir)
    
    #Bake and Set Bind Pose
    if selectedItems != None:
        for grp in selectedItems:
            str_parms=cmds.getAttr(grp+'.parms')
            parms = json.loads(str_parms)
            
            #Set FPS
            fps=parms[grp]['fps']
            fps_str=str(fps)+'fps'
            cmds.currentUnit(time=fps_str)
                
            #Set Frame Range 
            cmds.playbackOptions( minTime=parms[grp]['sf'], maxTime=parms[grp]['ef'] )
            
            #Bake

            if parms[grp]['tx'] or parms[grp]['ty'] or parms[grp]['tz'] or parms[grp]['rx'] or parms[grp]['ry'] or parms[grp]['rz'] or parms[grp]['sx'] or parms[grp]['sy'] or parms[grp]['sz']:
                bake(grp)
                
            #Bind Pose
            #if parms[grp]['bindpose']:
            #    fresh_bind(grp)

            #childNodes=cmds.listRelatives(grp,c=True,ad=True,type='transform',s=False,ni=True)
            #for cnode in childNodes:
            #    m = re.search(r"usdz", cnode)
            #    if m!=None:
            #        atchk=cmds.attributeQuery( 'name', node=cnode,ex=True)
            #        print atchk
            #        if atchk == False:
            #            cmds.addAttr( cnode, ln='name', dt='string' )
            #            cmds.setAttr( cnode+'.name', str(cnode)+'_'+name,type='string')

            name_atchk=cmds.attributeQuery( 'name', node=grp,ex=True)
            #print atchk
            if name_atchk == False:
                cmds.addAttr( grp, ln='name', dt='string' )
                cmds.setAttr( grp+'.name', str(grp)+'_'+name,type='string')

            selected_atchk=cmds.attributeQuery( 'selected', node=grp,ex=True)            
            #print atchk
            if selected_atchk == False:
                cmds.addAttr( grp, ln='selected', at='bool' )
                cmds.setAttr( grp+'.selected', 1)
            else:
                cmds.setAttr( grp+'.selected', 1)            

    #scrable
    scramble=cmds.checkBoxGrp(scramble_ins,q=True,v1=True)
    if scramble:
        scrambleScene()

    #Export
    objs=cmds.ls(v=True,tr=True,type='objectSet')


    #After Scrambling, we need to check name attribute to export proper asset.
    for obj in objs:
        atchk=cmds.attributeQuery( 'selected', node=obj,ex=True)
        if atchk:
            sel=cmds.getAttr(obj+'.selected')
            if sel==1:
                print(obj)
                #if re.search(grp, obj):
                #print(obj)
                #print(grp)
                cmds.select(cl=True)
                
                #childNodes=cmds.listRelatives(obj,c=True,ad=True,type='mesh',s=False,ni=True)
                childNodes=cmds.listRelatives(obj,c=True,ad=True,s=False,ni=True)
                print(childNodes)
                cmds.select(childNodes)
                #cmds.select(obj)
                
                str_parms=cmds.getAttr(obj+'.parms')
                parms = json.loads(str_parms)
                fmin=parms[obj]['sf']
                fmax=parms[obj]['ef']
                print(obj)
                #print fmax
                usdz_name=obj+'.usdz'
                filepath=os.path.join(dir,obj,usdz_name)
                print(filepath)
                export_anim_usdz(filepath,fmin,fmax)
                cmds.setAttr( obj+'.selected', 0)
                cmds.select(cl=True)


                              
def update_parms():
    #print grp_list
    selectedItems = cmds.textScrollList (src , query = True, selectItem = True)

    if selectedItems != None:
            for grp in selectedItems:
                atchk=cmds.attributeQuery( 'parms', node=grp,ex=True)
                if atchk == True:
                  str_parms=cmds.getAttr(grp+'.parms')
                  parms = json.loads(str_parms)

                  cmds.intSliderGrp(start_ins,e=True,v=parms[grp]['sf'])
                  cmds.intSliderGrp(end_ins,e=True,v=parms[grp]['ef'])
                  cmds.intSliderGrp(fps_ins,e=True,v=parms[grp]['fps'])
                  
                  cmds.checkBoxGrp(trans_ins,e=True,v1=parms[grp]['trans'])
                  cmds.checkBoxGrp(trans_ins,e=True,v2=parms[grp]['tx'])
                  cmds.checkBoxGrp(trans_ins,e=True,v3=parms[grp]['ty'])
                  cmds.checkBoxGrp(trans_ins,e=True,v4=parms[grp]['tz'])
    
                  cmds.checkBoxGrp(rot_ins,e=True,v1=parms[grp]['rot'])
                  cmds.checkBoxGrp(rot_ins,e=True,v2=parms[grp]['rx'])
                  cmds.checkBoxGrp(rot_ins,e=True,v3=parms[grp]['ry'])
                  cmds.checkBoxGrp(rot_ins,e=True,v4=parms[grp]['rz'])
    
                  cmds.checkBoxGrp(scale_ins,e=True,v1=parms[grp]['scale'])
                  cmds.checkBoxGrp(scale_ins,e=True,v2=parms[grp]['sx'])
                  cmds.checkBoxGrp(scale_ins,e=True,v3=parms[grp]['sy'])
                  cmds.checkBoxGrp(scale_ins,e=True,v4=parms[grp]['sz'])
                               
                  #cmds.checkBoxGrp(bp_ins,e=True,v1=parms[grp]['bindpose'])
                  #cmds.intSliderGrp(bindpose_frame_ins,e=True,en=parms[grp]['bindpose'])
                  #cmds.intSliderGrp(bindpose_frame_ins,e=True,v=parms[grp]['bindposef'])

        
    
cmds.window()
cmds.rowColumnLayout( numberOfColumns=1 )
#cmds.paneLayout()
# As we add contents to the window, align them vertically
#cmds.columnLayout( adjustableColumn=True )
#assets=cmds.ls(sl=True)
#src=cmds.textScrollList('srclist', numberOfRows=8, allowMultiSelection=True,append=assets,selectCommand='update_parms()', showIndexedItem=1)
src=cmds.textScrollList('srclist', numberOfRows=8, allowMultiSelection=True,selectCommand='update_parms()', showIndexedItem=1)

#for asset in assets:
#    cmds.textScrollList(src, e=True,si=asset)
#src=cmds.textScrollList (allowMultiSelection = True)

cmds.button(label='Add',command='add()')
cmds.button(label='Remove',command='rm()')
cmds.button(label='Clear',command='clr()')
cmds.columnLayout( adjustableColumn=True )
start_ins=cmds.intSliderGrp( field=True, label='Start Frame', minValue=0, maxValue=10, fieldMinValue=0, fieldMaxValue=10000, value=1,cc='set()')
end_ins=cmds.intSliderGrp( field=True, label='End Frame', minValue=0, maxValue=100, fieldMinValue=0, fieldMaxValue=1000000, value=60,cc='set()')
fps_ins=cmds.intSliderGrp( field=True, label='FPS', minValue=0, maxValue=60, fieldMinValue=0, fieldMaxValue=600, value=60,cc='set()')


trans_ins=cmds.checkBoxGrp( numberOfCheckBoxes=4, label='Translate', labelArray4=['trans','tx','ty','tz'] ,cc1='setbake()',cc2='set()',cc3='set()',cc4='set()')
rot_ins=cmds.checkBoxGrp( numberOfCheckBoxes=4, label='Rotation', labelArray4=['rot','rx','ry','rz'] ,cc1='setbake()',cc2='set()',cc3='set()',cc4='set()')
scale_ins=cmds.checkBoxGrp( numberOfCheckBoxes=4, label='Scale', labelArray4=['scale','sx','sy','sz'] ,cc1='setbake()',cc2='set()',cc3='set()',cc4='set()')
#bp_ins=cmds.checkBox(label='Bind Pose' ,cc='set()')
#bp_ins=cmds.checkBoxGrp( numberOfCheckBoxes=1, label='Bind Pose',cc1='set()')

#bindpose_frame_ins=cmds.intSliderGrp( field=True, label='Bind Pose Frame', minValue=1, maxValue=100, fieldMinValue=0, fieldMaxValue=10000, value=1,cc='set()',en=False)
scramble_ins=cmds.checkBoxGrp( numberOfCheckBoxes=1, label='Scramble')

grp_list={}

init()
update_parms()

'''
#Set last selected item in scrollList
if len(assets) > 0:
    #for asset in assets:
        #cmds.textScrollList(src, e=True,si=assets[0])
        #set()
        #cmds.textScrollList(src, e=True,di=asset)
    cmds.textScrollList(src, e=True,si=assets[len(assets)-1])
'''


# A button that does nothing
#cmds.button( label='Set',command='set()')
cmds.text( label='Output Directry' )
output_txt = cmds.textField()
outputDir=cmds.textField( output_txt, edit=True, tx="/Users/hiroyukiokubo/WORK/Projects/PencilPot/maya/usdz/")

cmds.button( label='Export',command='debug_show()',bgc=[0.7,0.7,0.7])
#cmds.button( label='Debug',command='debug_show()')



cmds.showWindow()



