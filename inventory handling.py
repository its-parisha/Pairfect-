import datetime

class PairfectInventory:
    """
    Inventory handling class for the 'Pairfect' digital twin system.
    Simulates inventory tracking and P&L computation.
    """
    def __init__(self):
        self.inventory = {}  # {item_name: {'quantity': int, 'cost_price': float, 'sale_price': float}}
        self.transactions = []  # List of dicts: {'type': 'buy'/'sell', 'item': str, 'quantity': int, 'price': float, 'date': datetime}
        self.total_revenue = 0.0
        self.total_cogs = 0.0  # Cost of Goods Sold

    def add_item(self, item_name, quantity, cost_price, sale_price):
        """Add or update an item in inventory."""
        if item_name in self.inventory:
            self.inventory[item_name]['quantity'] += quantity
            # Update average cost_price if needed (simple FIFO assumption here)
            self.inventory[item_name]['cost_price'] = (self.inventory[item_name]['cost_price'] * self.inventory[item_name]['quantity'] + cost_price * quantity) / (self.inventory[item_name]['quantity'] + quantity)
        else:
            self.inventory[item_name] = {'quantity': quantity, 'cost_price': cost_price, 'sale_price': sale_price}
        # Record transaction
        self.transactions.append({
            'type': 'buy',
            'item': item_name,
            'quantity': quantity,
            'price': cost_price * quantity,
            'date': datetime.datetime.now()
        })

    def remove_item(self, item_name, quantity):
        """Remove quantity from inventory (e.g., for sales or losses)."""
        if item_name in self.inventory and self.inventory[item_name]['quantity'] >= quantity:
            self.inventory[item_name]['quantity'] -= quantity
            cost = self.inventory[item_name]['cost_price'] * quantity
            self.total_cogs += cost
            # Record transaction
            self.transactions.append({
                'type': 'sell',
                'item': item_name,
                'quantity': quantity,
                'price': self.inventory[item_name]['sale_price'] * quantity,
                'date': datetime.datetime.now()
            })
            self.total_revenue += self.inventory[item_name]['sale_price'] * quantity
        else:
            raise ValueError(f"Insufficient stock for {item_name}")

    def sync_with_digital_twin(self, external_data):
        """
        Simulate syncing with a digital twin (e.g., from sensors or APIs).
        external_data: dict {item_name: {'quantity_adjust': int, 'cost_adjust': float}}
        """
        for item, adjustments in external_data.items():
            if item in self.inventory:
                self.inventory[item]['quantity'] += adjustments.get('quantity_adjust', 0)
                if 'cost_adjust' in adjustments:
                    self.inventory[item]['cost_price'] += adjustments['cost_adjust']
            else:
                # Assume default sale_price if new item
                self.add_item(item, adjustments.get('quantity_adjust', 0), adjustments.get('cost_adjust', 0), 0.0)

    def calculate_pnl(self):
        """Compute Profit and Loss statement."""
        gross_profit = self.total_revenue - self.total_cogs
        # Assuming no other expenses for simplicity; add more if needed
        net_profit = gross_profit
        return {
            'total_revenue': self.total_revenue,
            'total_cogs': self.total_cogs,
            'gross_profit': gross_profit,
            'net_profit': net_profit,
            'is_profit': net_profit > 0
        }

    def get_inventory_report(self):
        """Return current inventory status."""
        return self.inventory
