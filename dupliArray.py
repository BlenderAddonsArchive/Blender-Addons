
bl_info = {
    "name": "Duplicate Array",
    "description": "Copies active object or group instance into multiple duplicates, linked or not, along X and/or Y and/or Z axis, relative to local or global orientation",
    "author": "domlysz@gmail.com",
    "license': 'GPL',
    "version": (0, 1),
    "blender": (2, 7, 0),
    "location": "View3D > Object",
    "warning": "",
    "wiki_url": "https://github.com/domlysz",
    "tracker_url": "",
    "category": "Object"}

import bpy
from mathutils import Vector, Matrix

def getBBox(obj, applyTransform = True):
	if applyTransform:
		boundPts = [obj.matrix_world * Vector(corner) for corner in obj.bound_box]
	else:
		boundPts = obj.bound_box
	bbox={}
	bbox['xmin'] = min([pt[0] for pt in boundPts])
	bbox['xmax'] = max([pt[0] for pt in boundPts])
	bbox['ymin'] = min([pt[1] for pt in boundPts])
	bbox['ymax'] = max([pt[1] for pt in boundPts])
	bbox['zmin'] = min([pt[2] for pt in boundPts])
	bbox['zmax'] = max([pt[2] for pt in boundPts])
	return bbox


def getGroupBBox(objGroup, applyGroupTransform):
	group = objGroup.dupli_group
	bboxLst = []
	for obj in group.objects:
		boundPts = [obj.matrix_world * Vector(corner) for corner in obj.bound_box]
		if applyGroupTransform:
			boundPts = [objGroup.matrix_world * Vector(corner) for corner in boundPts]
		bbox={}
		bbox['xmin'] = min([pt[0] for pt in boundPts])
		bbox['xmax'] = max([pt[0] for pt in boundPts])
		bbox['ymin'] = min([pt[1] for pt in boundPts])
		bbox['ymax'] = max([pt[1] for pt in boundPts])
		bbox['zmin'] = min([pt[2] for pt in boundPts])
		bbox['zmax'] = max([pt[2] for pt in boundPts])
		bboxLst.append(bbox)
	gbbox={}
	gbbox['xmin'] = min([bbox['xmin'] for bbox in bboxLst])
	gbbox['xmax'] = max([bbox['xmax'] for bbox in bboxLst])
	gbbox['ymin'] = min([bbox['ymin'] for bbox in bboxLst])
	gbbox['ymax'] = max([bbox['ymax'] for bbox in bboxLst])
	gbbox['zmin'] = min([bbox['zmin'] for bbox in bboxLst])
	gbbox['zmax'] = max([bbox['zmax'] for bbox in bboxLst])

	return gbbox

def getDimsFromBbox(bbox):
	xDim=bbox['xmax']-bbox['xmin']
	yDim=bbox['ymax']-bbox['ymin']
	zDim=bbox['zmax']-bbox['zmin']
	return (xDim, yDim, zDim)

def dupliMove(vec, instance):#duplicate object preserve object transformation
	bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":instance, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":vec, "release_confirm":False})


def ToolsPanelExtension(self, context):
	self.layout.column(align=True).label(text="Addons:")
	self.layout.operator("object.multi_duplicate")

class OBJECT_OT_multiDuplicate(bpy.types.Operator):
	bl_idname = "object.multi_duplicate"
	bl_label = "Duplicate Array"
	bl_options = {"REGISTER", "UNDO"}
	#tool options
	xNb = bpy.props.IntProperty(name="", default=0, description="Number of copies", min=0, max=200, subtype="NONE")
	xSpace = bpy.props.FloatProperty(name = "")
	yNb = bpy.props.IntProperty(name="", default=0, description="Number of copies", min=0, max=200, subtype="NONE")
	ySpace = bpy.props.FloatProperty(name = "")
	zNb = bpy.props.IntProperty(name="", default=0, description="Number of copies", min=0, max=200, subtype="NONE")
	zSpace = bpy.props.FloatProperty(name = "")
	distType = bpy.props.EnumProperty(
		items = [("Space", "Space", ""), ("Total", "Total", "")],#(Key, Label, Description)
		name="Distance",
		description="")
	axis = bpy.props.EnumProperty(
		items = [("Global", "Global", ""), ("Local", "Local", "")],#(Key, Label, Description)
		name="Axis",
		description="")
	instance = bpy.props.BoolProperty(name="Instance", default=1)
	extraOffset = bpy.props.BoolProperty(name="Extra offset", default=0)
	xOffset = bpy.props.FloatProperty(name = "")
	yOffset = bpy.props.FloatProperty(name = "")
	zOffset = bpy.props.FloatProperty(name = "")
	xInv = bpy.props.BoolProperty(name="", default=0)
	yInv = bpy.props.BoolProperty(name="", default=0)
	zInv = bpy.props.BoolProperty(name="", default=0)

	def draw(self, context):
		layout = self.layout
		
		row = layout.row(align=True)
		row.alignment = 'LEFT'
		row.label("Axis")
		row.label("Number")
		row.label("Space")
		if self.distType == "Space":
			row.label("Inv.")
		
		row = layout.row(align=True)
		row.alignment = 'LEFT'
		row.label("X")
		row.prop(self, 'xNb')
		row.prop(self, 'xSpace')
		if self.distType == "Space":
			row.prop(self, 'xInv')
		
		row = layout.row(align=True)
		row.alignment = 'LEFT'
		row.label("Y")
		row.prop(self, 'yNb')
		row.prop(self, 'ySpace')
		if self.distType == "Space":
			row.prop(self, 'yInv')
		
		row = layout.row(align=True)
		row.alignment = 'LEFT'
		row.label("Z")
		row.prop(self, 'zNb')
		row.prop(self, 'zSpace')
		if self.distType == "Space":
			row.prop(self, 'zInv')

		layout.prop(self, 'distType')
		layout.prop(self, 'axis')
		layout.prop(self, 'instance')
		
		if self.distType == "Space":
			layout.prop(self, 'extraOffset')

		if self.extraOffset:
			row = layout.row(align=True)
			row.alignment = 'LEFT'
			row.label("X Offset")
			row.prop(self, 'xOffset')
			row = layout.row(align=True)
			row.alignment = 'LEFT'
			row.label("Y Offset")
			row.prop(self, 'yOffset')
			row = layout.row(align=True)
			row.alignment = 'LEFT'
			row.label("Z Offset")
			row.prop(self, 'zOffset')


	def invoke(self, context, event):#when click on operator button
		#Reset number of copy to 0
		self.xNb=0
		self.yNb=0
		self.zNb=0
		self.execute(context)
		return {'FINISHED'}

	def execute(self, context):#every times properties are modified
		#Parameters
		objs = bpy.context.selected_objects
		if not objs:
			self.report({'INFO'}, "There isn't active object")
			print("There isn't active object")
			return {'FINISHED'}
		#check if all objects are only group or only mesh
		nbMesh, nbGroup, nbOther = (0, 0, 0)
		for obj in objs:
			if obj.dupli_group:
				nbGroup+=1
			elif obj.type in ['MESH']:
				nbMesh+=1
			else:
				nbOther+=1
			if (nbGroup != 0 and nbMesh !=0) or nbOther !=0:
				self.report({'INFO'}, "Selected objects aren't only mesh or dupli group")
				print("Selected objects aren't only mesh or dupli group")
				return {'FINISHED'}
		#check if all objects are same instance or same dupli group
		if nbMesh == 0:#there is only dupli group
			if len(set([obj.dupli_group.name for obj in objs])) != 1:
				self.report({'INFO'}, "Selected objects aren't same instance")
				print("Selected objects aren't same instance")
				return {'FINISHED'}
		elif nbGroup == 0:#there is only mesh
			if len(set([obj.data.name for obj in objs])) != 1:
				self.report({'INFO'}, "Selected objects aren't same instance")
				print("Selected objects aren't same instance")
				return {'FINISHED'}
		#
		activeObj = objs[0]#context.active_object
		#
		if self.axis == "Local":
			applyTransform = False#bbox will be compute without object transform
			#objet transformation will be consider later into translation vector creation step
		else:#Global axis
			applyTransform = True#bbox will be compute according to object transform

		#Get bbox and dimensions
		if activeObj.dupli_group:
			bbox = getGroupBBox(activeObj, applyTransform)
		else:
			bbox=getBBox(activeObj, applyTransform)
		xDim, yDim, zDim = getDimsFromBbox(bbox)

		#Create Translation vector according to selected distance
		if self.distType == "Space":
			# manage axis and space direction
			if self.xInv : 
				xDim=-xDim
				if self.xSpace>0: self.xSpace=-self.xSpace
			else:
				if self.xSpace<0: self.xSpace=-self.xSpace
			if self.yInv : 
				yDim=-yDim
				if self.ySpace>0: self.ySpace=-self.ySpace
			else:
				if self.ySpace<0: self.ySpace=-self.ySpace
			if self.zInv : 
				zDim=-zDim
				if self.zSpace>0: self.zSpace=-self.zSpace
			else:
				if self.zSpace<0: self.zSpace=-self.zSpace
			# calculate vector
			if self.extraOffset:
				x = self.xSpace + xDim + self.xOffset
				y = self.ySpace + yDim + self.yOffset
				z = self.zSpace + zDim + self.zOffset
			else:
				x = self.xSpace + xDim
				y = self.ySpace + yDim
				z = self.zSpace + zDim
			xVec = Vector( (x, 0, 0) )
			yVec = Vector( (0, y, 0) )
			zVec = Vector( (0, 0, z) )
		else:
			xVec = Vector( (self.xSpace, 0, 0) )
			yVec = Vector( (0, self.ySpace, 0) )
			zVec = Vector( (0, 0, self.zSpace) )

		#Apply object rotation and scale to translation vector, in this way translation will be do along local axis
		#and object transformation will be taken into account
		if self.axis == "Local":
			matrix=activeObj.matrix_world.copy()
			matrix[0][3], matrix[1][3], matrix[2][3] = 0, 0, 0#set translation component of matrix to zero
			xVec = matrix * xVec
			yVec = matrix * yVec 
			zVec = matrix * zVec 

		#Perform copies
		copies = []
		copies.extend(context.selected_objects)
		# x copies
		for i in range(self.xNb):
			dupliMove(xVec, self.instance)
			copies.extend(context.selected_objects)
		# seclect all copies
		for obj in copies:
			obj.select=True
		# y copies
		for i in range(self.yNb):
			dupliMove(yVec, self.instance)
			copies.extend(context.selected_objects)
		# select all copies
		for obj in copies:
			obj.select=True
		# z copies
		for i in range(self.zNb):
			dupliMove(zVec, self.instance)
			copies.extend(context.selected_objects)
		# select all copies
		for obj in copies:
			obj.select=True

		return {'FINISHED'}

def register():
	bpy.utils.register_module(__name__)
	#append
	bpy.types.VIEW3D_PT_tools_object.append(ToolsPanelExtension)

def unregister():
	bpy.utils.unregister_module(__name__)
	#rmv append
	bpy.types.VIEW3D_PT_tools_object.remove(ToolsPanelExtension)

if __name__ == '__main__':
	register()
