from flask import Blueprint, request, jsonify
from app import db
from models import MenuCategory, MenuItem

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/menu', methods=['GET'])
def get_full_menu():
    """
    Get the complete menu with all categories and their items
    Returns menu organized by categories as specified in requirements
    """
    try:
        # Get all active categories ordered by display_order
        categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()
        
        menu_data = []
        for category in categories:
            # Get all available items for this category
            items = MenuItem.query.filter_by(
                category_id=category.category_id,
                is_available=True
            ).order_by(MenuItem.display_order).all()
            
            category_data = {
                'category_id': category.category_id,
                'category_name': category.category_name,
                'display_order': category.display_order,
                'items': [item.to_dict() for item in items]
            }
            menu_data.append(category_data)
        
        return jsonify({
            'menu': menu_data,
            'total_categories': len(menu_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@menu_bp.route('/menu/categories', methods=['GET'])
def get_categories():
    """
    Get all menu categories
    """
    try:
        categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()
        return jsonify({
            'categories': [cat.to_dict() for cat in categories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@menu_bp.route('/menu/category/<int:category_id>', methods=['GET'])
def get_category_items(category_id):
    """
    Get all items for a specific category
    """
    try:
        category = MenuCategory.query.get(category_id)
        if not category or not category.is_active:
            return jsonify({'error': 'Category not found'}), 404
        
        items = MenuItem.query.filter_by(
            category_id=category_id,
            is_available=True
        ).order_by(MenuItem.display_order).all()
        
        return jsonify({
            'category': category.to_dict(),
            'items': [item.to_dict() for item in items]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@menu_bp.route('/menu/item/<int:item_id>', methods=['GET'])
def get_menu_item(item_id):
    """
    Get details for a specific menu item
    """
    try:
        item = MenuItem.query.get(item_id)
        if not item or not item.is_available:
            return jsonify({'error': 'Menu item not found'}), 404
        
        return jsonify(item.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@menu_bp.route('/menu/search', methods=['GET'])
def search_menu_items():
    """
    Search menu items by name or description
    Query parameter: q (search term)
    """
    try:
        search_term = request.args.get('q', '').strip()
        if not search_term:
            return jsonify({'error': 'Search term is required'}), 400
        
        # Search in item names and descriptions
        items = MenuItem.query.filter(
            db.and_(
                MenuItem.is_available == True,
                db.or_(
                    MenuItem.item_name.ilike(f'%{search_term}%'),
                    MenuItem.description.ilike(f'%{search_term}%')
                )
            )
        ).order_by(MenuItem.item_name).all()
        
        return jsonify({
            'search_term': search_term,
            'results_count': len(items),
            'items': [item.to_dict() for item in items]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500 