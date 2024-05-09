bl_info = {
	"name": "Move Origin to Surface",
	"author": "Johan Basberg",
	"version": (2, 0),
	"blender": (2, 80, 0),
	"location": "Right Click > Move Origin to Selection",
	"description": "Moves origin to center of selection being edited.",
	"category": "Object",
}

import bpy
import bmesh
from mathutils import Vector

class MoveOriginToSurfaceOperator(bpy.types.Operator):
	bl_idname = "object.move_origin_to_surface"
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
		obj = context.active_object

		# Get the mesh data
		mesh = obj.data

		# Create a BMesh representation of the mesh
		bm = bmesh.new()
		bm.from_mesh(mesh)

		# Retain 3D cursor position to restore it after
		tmp_cursor_location = Vector(bpy.context.scene.cursor.location)

		# Get selected vertices
		selected_verts = [v.co for v in bpy.context.active_object.data.vertices if v.select]

		# Calculate the average center point if there are multiple selected edges
		if not selected_verts:
			self.report({'ERROR'}, "Please ensure at least one vertex, edge or face is selected.")
			bm.free()
			return {'CANCELLED'}

		# Calculate the average
		center = Vector()
		for vert in selected_verts:
			center += vert
		center /= len(selected_verts)

		bpy.context.scene.cursor.location = obj.matrix_world @ center

		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
		bpy.ops.object.mode_set(mode='EDIT')

		# Restore location of 3D cursor
		bpy.context.scene.cursor.location = tmp_cursor_location

		# Free the BMesh
		bm.free()




def menu_func(self, context):
	self.layout.separator()
	selected_icon = "TRANSFORM_ORIGINS"
	self.layout.operator(MoveOriginToSurfaceOperator.bl_idname, text="Move Origin to Selection", icon=selected_icon)

def register():
	bpy.utils.register_class(MoveOriginToSurfaceOperator)
	bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(menu_func)

def unregister():
	bpy.utils.unregister_class(MoveOriginToSurfaceOperator)
	bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(menu_func)

if __name__ == "__main__":
	register()
