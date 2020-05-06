from db import db
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims, fresh_jwt_required
from models.item import ItemModel

class Item(Resource): 
	# to get json payload through regparse 
	parser = reqparse.RequestParser()
	parser.add_argument('price',
			type=float,
			required=True,
			help='This field can not blank'
	)
	parser.add_argument('store_id',
			type=int,
			required=True,
			help='every item needs a store id'
	)

	@jwt_required
	def get(self, name): # single item 
		item = ItemModel.find_by_name(name)
		if item:
			return item.json()

		return {'message': 'there is no item name <<{}>> in the database.'.format(name)}, 404
		
	@fresh_jwt_required
	def post(self, name):
		if ItemModel.find_by_name(name):

			return {'message': ' <<{}>> already exists.'.format(name)}, 400
		
		data = Item.parser.parse_args() 

		item = ItemModel(name, **data) #data['price'], data['store_id']

		try:
			item.save_to_db()

		except:

			return {'message': 'An error accurred inserting the item'}, 500
		return item.json(), 201 

	@jwt_required
	def delete(self, name):
		claims = get_jwt_claims()
		if not claims['is_admin']:
			return {'message': 'Admin privilege is required'}, 401

		item = ItemModel.find_by_name(name)
		if item:
			item.delete_from_db()

		return {'message': '{} was deleted!'.format(name)}

	def put(self, name):
		
		data = Item.parser.parse_args() 

		item = ItemModel.find_by_name(name) # this is the item object
		
		if item is None:

			item = ItemModel(name, **data) # data['price'], data['store_id']

		else:

			item.price = data['price']

		item.save_to_db()

		return item.json()


class ItemList(Resource):
	def get(self):
		
		return {'items': [item.json() for item in ItemModel.find_all()]}

		