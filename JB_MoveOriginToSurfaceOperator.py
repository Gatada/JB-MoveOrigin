bl_info = {
	"name": "Move Origin to Selection",
	"author": "Johan Basberg",
	"version": (2, 2),
	"blender": (2, 80, 0),
	"location": "Right Click > Move Origin to Selection",
	"description": "Moves origin to center of selection being edited.",
	"category": "Object",
}

import bpy
import bmesh
from mathutils import Vector

class JB_MoveOriginToSelectionOperator(bpy.types.Operator):
	bl_idname = "jb_moveorigintoselectionoperator.move_origin_to_selection"
	bl_label = "Move Origin to Selection"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return obj and obj.type == 'MESH' and obj.mode == 'EDIT'


	def execute(self, context):

		# Force a context update
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.mode_set(mode='EDIT')

		# Get selection mode based on property value
		selection_mode = bpy.context.tool_settings.mesh_select_mode[:]

		self.move_origin_to_vertices(context)

		return {'FINISHED'}


	def move_origin_to_vertices(self, context):
		selected_verts = []

		# Iterate over all selected objects in edit mode
		for obj in context.selected_objects:
			if obj.mode == 'EDIT':
				# Get the mesh data
				mesh = obj.data

				# Create a BMesh representation of the mesh
				bm = bmesh.new()
				bm.from_mesh(mesh)

				# Get selected vertices
				# verts = [v.co for v in bm.verts if v.select]
				verts = [obj.matrix_world @ v.co for v in bm.verts if v.select]

				# Append vertices to selected_verts
				selected_verts.extend(verts)

				# Free the BMesh
				bm.free()

		# Calculate the average center point if there are multiple selected edges
		if not selected_verts:
			bm.free()
			self.report({'ERROR'}, "No vertex, edge or face selected!")
			return {'CANCELLED'}

		# Retain 3D cursor position to restore it after
		tmp_cursor_location = Vector(bpy.context.scene.cursor.location)

		# Calculate the average
		global_center = Vector()
		for vert in selected_verts:
			global_center += vert
		global_center /= len(selected_verts)

		bpy.context.scene.cursor.location = global_center

		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
		bpy.ops.object.mode_set(mode='EDIT')

		# Restore location of 3D cursor
		bpy.context.scene.cursor.location = tmp_cursor_location

		return {'FINISHED'}


def menu_func(self, context):
	self.layout.separator()
	selected_icon = "TRANSFORM_ORIGINS"
	self.layout.operator(JB_MoveOriginToSelectionOperator.bl_idname, text="Move Origin to Selection", icon=selected_icon)


def register():
	bpy.utils.register_class(JB_MoveOriginToSelectionOperator)
	bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(menu_func)


def unregister():
	bpy.utils.unregister_class(JB_MoveOriginToSelectionOperator)
	bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(menu_func)


if __name__ == "__main__":
	register()
