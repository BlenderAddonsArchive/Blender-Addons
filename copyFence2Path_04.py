bl_info = {
    "name": "CopyFence2Path",
    "description": "Copies fence to path",
    'author': 'domLysz',
    'license': 'GPL',
    "version": (0, 4),
    "blender": (2, 7, 0),
    "location": "View3D > Object",
    "warning": "",
    "wiki_url": "https://github.com/domlys",
    "tracker_url": "",
    "category": "Object"}

import bpy
from bpy.props import *
import math
from mathutils import Vector, Matrix


def dupliMove(vec, instance):#duplicate object preserve object transformation
	bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":instance, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":vec, "release_confirm":False})

def offsetPtAlongVec(pt, vec, dst):
	pourcentOffset = dst / vec.length
	return pt + pourcentOffset * vec


def findBestSizeIncrease(length, offsetInit, eps, step, maxIncreaseFactor):
	offset=offsetInit
	r=length%offset
	while r > eps:
		if offset>offsetInit*maxIncreaseFactor:
			return False
		offset+=step
		r=length%offset
	return offset

def findBestSizeDecrease(length, offsetInit, eps, step, maxDecreaseFactor):
	offset=offsetInit
	r=length%offset
	while r > eps:
		if offset<offsetInit*maxDecreaseFactor:
			return False
		offset-=step
		r=length%offset
	delta=offsetInit-offset
	return offset

class ToolsPanelCopyFence(bpy.types.Panel):
	bl_category = "Tools"
	bl_label = "Copy fence"
	bl_space_type = "VIEW_3D"
	bl_context = "objectmode"
	bl_region_type = "TOOLS"

	def draw(self, context):
		self.layout.operator("object.copy_fence")


class OBJECT_OT_copyFenceAlongPath(bpy.types.Operator):
	bl_idname = "object.copy_fence"
	bl_label = "Copy fence along path"
	bl_options = {"REGISTER", "UNDO"}
	#Operator options
	strategy = EnumProperty(
			items = [("1", "All copies", "Resizer all copies to match a segment length"), ("2", "Last copy", "Rezise only last copy of a segment to match length")],
			name="Resize strategy",
			description="How to optimize size of copies")

	def execute(self, context):#every times properties are modified
		#get Selected obj
		objs = bpy.context.selected_objects
		#check number of selected objs
		if not objs or len(objs) < 2:
			self.report({'INFO'}, "Pre-selection is incorrect")
			print("Pre-selection is incorrect")
			return {'FINISHED'}
		#check if selected obj is correct (only one mesh & one curve)
		types = set( (objs[0].type, objs[1].type ))
		if types != set( ('MESH','CURVE') ):
			self.report({'INFO'}, "Pre-selection is incorrect")
			print("Pre-selection is incorrect")
			return {'FINISHED'}
		#allocate obj
		for obj in objs:
			if obj.type == 'MESH': mesh = obj
			if obj.type == 'CURVE': curve = obj
		curve.select=False
		bpy.context.scene.objects.active = mesh
		bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		#Get dimensions
		offset=mesh.dimensions.x#*mesh.scale.x

		spline=curve.data.splines[0]#?
		if len(spline.bezier_points) < 2:
			self.report({'INFO'}, "Spline incorrect")
			print("Spline incorrect")
			return {'FINISHED'}

		segments = len(spline.bezier_points)
		if not spline.use_cyclic_u:
			segments -= 1

		for i in range(segments):
			v1 = (spline.bezier_points[i].co * curve.matrix_world) + curve.location #matrix_world doesn't apply location !?
			v2 = (spline.bezier_points[i+1].co * curve.matrix_world) + curve.location
			v3 = (v2-v1)
			totalDst=v3.length#The distance between 2 vec can be calculated by subracting 2 vectors and printing the length of the resultant vector
			refVec=Vector((1,0))
			angle=v3.xy.angle_signed(refVec)#angle_signed method expects a 2D-Vector
			#print(totalDst, math.degrees(angle))

			adjustLast=False
			eps=0.005#5cm
			if self.strategy == '1':
				#Find best size
				step=0.0001#1mm
				maxIncreaseFactor=2
				maxDecreaseFactor=0.5
				bestSize1=findBestSizeIncrease(totalDst, offset, eps, step, maxIncreaseFactor)
				bestSize2=findBestSizeDecrease(totalDst, offset, eps, step, maxDecreaseFactor)
				#Choose best size
				if not bestSize1 and not bestSize2:
					print("Can't optimize mesh size for segment number "+str(i))
					bestSize=offset
					adjustLast=True#the last copy in this segments will be adjusted
				elif not bestSize1: bestSize=bestSize2
				elif not bestSize2: bestSize=bestSize1
				elif abs(offset-bestSize1) < abs(offset-bestSize2):
					bestSize=bestSize1
				else:
					bestSize=bestSize2
			else:
				#Resize last only
				bestSize=offset
				adjustLast=True#the last copy in this segments will be adjusted

			currentDst=0
			while currentDst < totalDst-eps:
				#Get initial obj
				mesh.select=True
				bpy.context.scene.objects.active = mesh
				#Compute translation vector
				destinationLoc = offsetPtAlongVec(v1, v3, currentDst)
				vec=destinationLoc-mesh.location
				#Duplicate initial obj
				dupliMove(vec, instance=True)
				#update distance
				currentDst+=bestSize
				#Adjust rotation
				obj = bpy.context.active_object
				obj.rotation_euler= (0,0,angle)
				#Adjust scale
				if not adjustLast:
					scale=bestSize/offset
					obj.scale.x=scale
				else:
					nextDst=currentDst+offset
					exceedLimit=(3/4)*offset
					if nextDst > totalDst and nextDst-totalDst > exceedLimit:#next copy va dépasser de + de exceedLimit
						#Dans ce cas agrandir la copie actuelle (au max l'agrandissement sera ici de +1/4)
						exceedDst=nextDst-totalDst
						coverdst=offset-exceedDst
						targetSize=offset+coverdst
						scale=targetSize/offset
						obj.scale.x=scale
						currentDst=totalDst#exit loop
					if currentDst > totalDst:#copie actuelle dépasse de la ligne (forcement de - de exceedLimit vue qu'on traite à l'avance les autres cas)
						#Dans ce cas réduire la copie actuelle (au max la réduction sera de -3/4)
						exceedDst=currentDst-totalDst
						targetSize=offset-exceedDst
						scale=coverdst/offset#decrease size
						obj.scale.x=scale
				#
				obj.select=False


		return {'FINISHED'}

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == '__main__':
	register()
