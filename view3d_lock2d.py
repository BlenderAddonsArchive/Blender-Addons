
bl_info = {
	'name': 'Lock 3d navigation to 2d',
	'author': 'domLysz',
	'license': 'GPL',
	'deps': '',
	'version': (0, 1),
	'blender': (2, 7, 0),
	'location': 'Shortcut numpad *',
	'description': '',
	'warning': '',
	'wiki_url': 'https://github.com/domlysz',
	'tracker_url': '',
	'link': '',
	'support': 'COMMUNITY',
	'category': 'View 3d',
	}

import bpy

class LOCK2D(bpy.types.Operator):

	bl_idname = "view3d.lock2d"
	bl_description = 'Pan 3D view with mouse whell clic and shift to rotate'
	bl_label = "Lock 2d"

	def execute(self, context):
		wm = bpy.context.window_manager
		km = wm.keyconfigs.active.keymaps['3D View']
		kmiRotate = km.keymap_items['view3d.rotate']
		kmiMove = km.keymap_items['view3d.move']
		kmiRotate.shift = not kmiRotate.shift
		kmiMove.shift = not kmiMove.shift
		return {'FINISHED'}

def register():
	bpy.utils.register_class(LOCK2D)
	wm = bpy.context.window_manager
	km = wm.keyconfigs.active.keymaps['3D View']
	kmi = km.keymap_items.new(idname='view3d.lock2d', value='PRESS', type='NUMPAD_ASTERIX', ctrl=False, alt=False, shift=False, oskey=False)

def unregister():
	wm = bpy.context.window_manager
	km = wm.keyconfigs.active.keymaps['3D View']
	kmi = km.keymap_items.remove(km.keymap_items['view3d.lock2d'])
	bpy.utils.unregister_class(LOCK2D)
