bl_info = {
	"name": "Set custom transform orientation",
	"description": "",
	'author': 'domLysz',
	'license': 'GPL',
	"version": (0, 1),
	"blender": (2, 6, 8),
	"location": "View3D > Numeric",
	"warning": "",
	"wiki_url": "https://github.com/domlysz",
	"tracker_url": "",
	"category": "3D View"}

import bpy
from bpy.props import FloatVectorProperty
from bpy.types import Operator


class VIEW3D_OT_set_cto(bpy.types.Operator):
	bl_idname = "view3d.set_cto"
	bl_label = "Set custom transform orientation rotation (°)"
	bl_options = {"REGISTER", "UNDO"}

	cto = FloatVectorProperty(name = "", subtype='EULER')

	def invoke(self, context, event):#when click on operator button
		view = bpy.context.space_data
		self.cto = view.current_orientation.matrix.to_euler()
		self.execute(context)
		context.window_manager.invoke_props_popup(self, event)
		return {'RUNNING_MODAL'}

	def draw(self, context):
		layout = self.layout
		col = layout.column()
		col.prop(self, "cto", text="")

	def execute(self, context):#every times properties are modified
		view = context.space_data
		view.current_orientation.matrix = self.cto.to_matrix()
		return {'FINISHED'}

#function to extend current "transform orientation" panel
def TO_panel_extension(self, context):
	layout = self.layout
	view = context.space_data
	if view.transform_orientation not in ['GLOBAL', 'LOCAL', 'GIMBAL', 'NORMAL', 'VIEW']:
		row = layout.row()
		row.operator("view3d.set_cto", text="Set rotation")

def register():
	bpy.utils.register_module(__name__)
	#append to existing panel
	bpy.types.VIEW3D_PT_transform_orientations.append(TO_panel_extension)

def unregister():
	bpy.utils.unregister_module(__name__)
	#remove append
	bpy.types.VIEW3D_PT_transform_orientations.remove(TO_panel_extension)

if __name__ == '__main__':
	register()
