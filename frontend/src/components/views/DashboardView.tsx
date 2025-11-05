import React from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Package, LogOut, Plus, Grid3X3, Search, MessageSquare, Eye, Edit, Trash2, Loader2 } from "lucide-react"
import { type User, type InventoryItem, apiService } from "@/lib/api"

interface DashboardViewProps {
  user: User
  inventory: InventoryItem[]
  loading: boolean
  error: string | null
  onViewChange: (view: string) => void
  onLogout: () => void
  onRetryLoad: () => void
}

export function DashboardView({ 
  user, 
  inventory, 
  loading, 
  error, 
  onViewChange, 
  onLogout, 
  onRetryLoad 
}: DashboardViewProps) {
  return (
    <div className="min-h-screen bg-background">
      <div className="flex">
        {/* Sidebar */}
        <div className="w-64 bg-sidebar border-r border-sidebar-border p-4">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-sidebar-primary rounded-lg flex items-center justify-center">
              <Package className="w-6 h-6 text-sidebar-primary-foreground" />
            </div>
            <div>
              <h1 className="font-bold text-sidebar-foreground">DIY Finder</h1>
              <p className="text-sm text-muted-foreground">Welcome, {user?.username}</p>
            </div>
          </div>

          <nav className="space-y-2">
            <Button variant="ghost" className="w-full justify-start gap-3" onClick={() => onViewChange("dashboard")}>
              <Grid3X3 className="w-4 h-4" />
              Dashboard
            </Button>
            <Button variant="ghost" className="w-full justify-start gap-3" onClick={() => onViewChange("add-item")}>
              <Plus className="w-4 h-4" />
              Add Item
            </Button>
            <Button variant="ghost" className="w-full justify-start gap-3" onClick={() => onViewChange("search")}>
              <Search className="w-4 h-4" />
              Search
            </Button>
            <Button variant="ghost" className="w-full justify-start gap-3" onClick={() => onViewChange("chat")}>
              <MessageSquare className="w-4 h-4" />
              Chat
            </Button>
          </nav>

          <div className="mt-auto pt-8">
            <Button
              variant="ghost"
              className="w-full justify-start gap-3 text-muted-foreground"
              onClick={onLogout}
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </Button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6">
          <div className="max-w-6xl mx-auto">
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-balance mb-2">Your Inventory</h2>
              <p className="text-muted-foreground text-pretty">
                Manage your garage and workshop items with AI-powered organization
              </p>
            </div>

            {/* Error Display */}
            {error && (
              <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                <div className="flex items-center gap-2 text-destructive">
                  <span className="text-sm font-medium">Error loading inventory:</span>
                  <span className="text-sm">{error}</span>
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="mt-2"
                  onClick={onRetryLoad}
                >
                  Try Again
                </Button>
              </div>
            )}

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                      <Package className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">{inventory.length}</p>
                      <p className="text-sm text-muted-foreground">Total Items</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                      <Grid3X3 className="w-6 h-6 text-accent" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">3</p>
                      <p className="text-sm text-muted-foreground">Categories</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center gap-2">
                    <Button onClick={() => onViewChange("add-item")} className="flex-1">
                      <Plus className="w-4 h-4 mr-2" />
                      Add New Item
                    </Button>
                    <Button variant="outline" onClick={() => onViewChange("search")}>
                      <Search className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Inventory Grid */}
            {loading ? (
              <div className="col-span-full flex items-center justify-center py-12">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-6 h-6 animate-spin" />
                  <span>Loading inventory...</span>
                </div>
              </div>
            ) : inventory.length === 0 ? (
              <div className="col-span-full text-center py-12">
                <Package className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No items yet</h3>
                <p className="text-muted-foreground mb-4">Start building your inventory by adding your first DIY item</p>
                <Button onClick={() => onViewChange("add-item")}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Your First Item
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {inventory.map((item) => (
                <Card key={item.id} className="overflow-hidden">
                  <div className="aspect-square bg-muted relative">
                    {item.image_data ? (
                      <img
                        src={item.image_data}
                        alt={item.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <Package className="w-16 h-16 text-muted-foreground" />
                      </div>
                    )}
                    <div className="absolute top-2 right-2">
                      <Badge variant="default" className="bg-primary text-primary-foreground font-semibold">
                        {item.quantity}
                      </Badge>
                    </div>
                  </div>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-balance">{item.name}</h3>
                      <div className="flex gap-1">
                        <Button size="sm" variant="ghost">
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="ghost">
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button 
                          size="sm" 
                          variant="ghost"
                          onClick={async () => {
                            if (window.confirm(`Are you sure you want to delete "${item.name}"?`)) {
                              try {
                                const response = await apiService.deleteItem(item.id, user.username);
                                if (response.success) {
                                  onRetryLoad(); // Refresh the inventory list
                                } else {
                                  alert(`Failed to delete item: ${response.error}`);
                                }
                              } catch (err) {
                                alert(`Error deleting item: ${err instanceof Error ? err.message : 'Unknown error'}`);
                              }
                            }
                          }}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3 text-pretty">
                      {item.description || "No description available"}
                    </p>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm">
                        <span className="font-medium">Category:</span>
                        <Badge variant="outline">{item.category}</Badge>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <span className="font-medium">Location:</span>
                        <span className="text-muted-foreground">{item.location || "Unknown"}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <span className="font-medium">Storage:</span>
                        <span className="text-muted-foreground">{item.storage_box || "General"}</span>
                      </div>
                      {item.brand && (
                        <div className="flex items-center gap-2 text-sm">
                          <span className="font-medium">Brand:</span>
                          <span className="text-muted-foreground">{item.brand}</span>
                        </div>
                      )}
                      {item.size && (
                        <div className="flex items-center gap-2 text-sm">
                          <span className="font-medium">Size:</span>
                          <span className="text-muted-foreground">{item.size}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-2 text-sm">
                        <span className="font-medium">Quantity:</span>
                        <Badge variant="secondary" className="text-xs">{item.quantity} pieces</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
