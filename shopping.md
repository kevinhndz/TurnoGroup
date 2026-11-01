You are given a task to integrate an existing React component in the codebase

The codebase should support:
- shadcn project structure  
- Tailwind CSS
- Typescript

If it doesn't, provide instructions on how to setup project via shadcn CLI, install Tailwind or Typescript.

Determine the default path for components and styles. 
If default path for components is not /components/ui, provide instructions on why it's important to create this folder
Copy-paste this component to /components/ui folder:
```tsx
drawer.tsx
'use client';

import * as React from 'react';
import { Drawer as DrawerPrimitive } from 'vaul';
import { cn } from '@/lib/utils';

function Drawer({
	...props
}: React.ComponentProps<typeof DrawerPrimitive.Root>) {
	return <DrawerPrimitive.Root data-slot="drawer" {...props} />;
}

function DrawerTrigger({
	...props
}: React.ComponentProps<typeof DrawerPrimitive.Trigger>) {
	return <DrawerPrimitive.Trigger data-slot="drawer-trigger" {...props} />;
}

function DrawerPortal({
	...props
}: React.ComponentProps<typeof DrawerPrimitive.Portal>) {
	return <DrawerPrimitive.Portal data-slot="drawer-portal" {...props} />;
}

function DrawerClose({
	...props
}: React.ComponentProps<typeof DrawerPrimitive.Close>) {
	return <DrawerPrimitive.Close data-slot="drawer-close" {...props} />;
}

function DrawerOverlay({
	className,
	...props
}: React.ComponentProps<typeof DrawerPrimitive.Overlay>) {
	return (
		<DrawerPrimitive.Overlay
			data-slot="drawer-overlay"
			className={cn(
				'data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 bg-background/50 fixed inset-0 z-50 backdrop-blur',
				className,
			)}
			{...props}
		/>
	);
}

function DrawerContent({
	className,
	children,
	...props
}: React.ComponentProps<typeof DrawerPrimitive.Content>) {
	return (
		<DrawerPortal data-slot="drawer-portal">
			<DrawerOverlay />
			<DrawerPrimitive.Content
				data-slot="drawer-content"
				className={cn(
					'group/drawer-content bg-background fixed z-50 flex h-auto flex-col',
					'data-[vaul-drawer-direction=top]:inset-x-0 data-[vaul-drawer-direction=top]:top-0 data-[vaul-drawer-direction=top]:mb-24 data-[vaul-drawer-direction=top]:max-h-[80vh] data-[vaul-drawer-direction=top]:rounded-b-3xl data-[vaul-drawer-direction=top]:border-b',
					'data-[vaul-drawer-direction=bottom]:inset-x-0 data-[vaul-drawer-direction=bottom]:bottom-0 data-[vaul-drawer-direction=bottom]:mt-24 data-[vaul-drawer-direction=bottom]:max-h-[80vh] data-[vaul-drawer-direction=bottom]:rounded-t-3xl data-[vaul-drawer-direction=bottom]:border-t',
					'data-[vaul-drawer-direction=right]:inset-y-0 data-[vaul-drawer-direction=right]:right-0 data-[vaul-drawer-direction=right]:w-3/4 data-[vaul-drawer-direction=right]:border-l data-[vaul-drawer-direction=right]:sm:max-w-sm',
					'data-[vaul-drawer-direction=left]:inset-y-0 data-[vaul-drawer-direction=left]:left-0 data-[vaul-drawer-direction=left]:w-3/4 data-[vaul-drawer-direction=left]:border-r data-[vaul-drawer-direction=left]:sm:max-w-sm',
					className,
				)}
				{...props}
			>
				<div className="bg-muted mx-auto my-2 hidden h-2 w-24 shrink-0 rounded-full group-data-[vaul-drawer-direction=bottom]/drawer-content:block" />

				{children}
			</DrawerPrimitive.Content>
		</DrawerPortal>
	);
}

function DrawerHeader({ className, ...props }: React.ComponentProps<'div'>) {
	return (
		<div
			data-slot="drawer-header"
			className={cn(
				'flex w-full flex-col gap-1 rounded-t-3xl border-b px-4 py-2 md:mx-auto md:max-w-md',
				className,
			)}
			{...props}
		/>
	);
}

function DrawerBody({ className, ...props }: React.ComponentProps<'div'>) {
	return (
		<div
			data-slot="drawer-body"
			className={cn('w-full px-4 py-6 md:mx-auto md:max-w-md', className)}
			{...props}
		/>
	);
}

function DrawerFooter({ className, ...props }: React.ComponentProps<'div'>) {
	return (
		<div
			data-slot="drawer-footer"
			className={cn(
				'mt-auto grid w-full gap-2 border-t px-4 py-3 md:mx-auto md:max-w-md',
				className,
			)}
			{...props}
		/>
	);
}

function DrawerTitle({
	className,
	...props
}: React.ComponentProps<typeof DrawerPrimitive.Title>) {
	return (
		<DrawerPrimitive.Title
			data-slot="drawer-title"
			className={cn('text-foreground font-heading font-medium', className)}
			{...props}
		/>
	);
}

function DrawerDescription({
	className,
	...props
}: React.ComponentProps<typeof DrawerPrimitive.Description>) {
	return (
		<DrawerPrimitive.Description
			data-slot="drawer-description"
			className={cn('text-muted-foreground text-sm', className)}
			{...props}
		/>
	);
}

export {
	Drawer,
	DrawerPortal,
	DrawerOverlay,
	DrawerTrigger,
	DrawerClose,
	DrawerContent,
	DrawerHeader,
	DrawerBody,
	DrawerFooter,
	DrawerTitle,
	DrawerDescription,
};


demo.tsx
'use client';

import * as React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
	Drawer,
	DrawerBody,
	DrawerClose,
	DrawerContent,
	DrawerDescription,
	DrawerFooter,
	DrawerHeader,
	DrawerTitle,
	DrawerTrigger,
} from '@/components/ui/drawer';
import { 
	Minus, 
	Plus, 
	ShoppingCart,
	Trash2,
} from 'lucide-react';


export default function ShoppingCartDrawer() {
	const [cartItems, setCartItems] = React.useState([
		{
			id: 1,
			name: 'Headphones',
			price: 79.99,
			quantity: 1,
			image: '🎧'
		},
		{
			id: 3,
			name: 'Phone Case',
			price: 24.99,
			quantity: 1,
			image: '📱'
		}
	]);

	const updateQuantity = (id: number, newQuantity: number) => {
		if (newQuantity === 0) {
			setCartItems(prev => prev.filter(item => item.id !== id));
		} else {
			setCartItems(prev =>
				prev.map(item =>
					item.id === id ? { ...item, quantity: newQuantity } : item
				)
			);
		}
	};

	const removeItem = (id: number) => {
		setCartItems(prev => prev.filter(item => item.id !== id));
	};

	const getTotalPrice = () => {
		return cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);
	};

	const getTotalItems = () => {
		return cartItems.reduce((total, item) => total + item.quantity, 0);
	};

	return (
		<Drawer>
			<DrawerTrigger asChild>
				<Button variant="outline" className="relative">
					<ShoppingCart className="w-4 h-4 mr-2" />
					Shopping Cart
					{cartItems.length > 0 && (
						<span className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 text-xs flex items-center justify-center">
							{getTotalItems()}
						</span>
					)}
				</Button>
			</DrawerTrigger>
			<DrawerContent>
				<DrawerHeader>
					<DrawerTitle className="flex items-center gap-2">
						<ShoppingCart className="w-5 h-5" />
						Shopping Cart ({getTotalItems()} items)
					</DrawerTitle>
					<DrawerDescription>
						Review your items before checkout.
					</DrawerDescription>
				</DrawerHeader>
				<DrawerBody className="max-h-[60vh] overflow-y-auto">
					{cartItems.length === 0 ? (
						<div className="text-center py-8">
							<ShoppingCart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
							<p className="text-gray-500 mb-4">Your cart is empty</p>
							<Button variant="outline">Continue Shopping</Button>
						</div>
					) : (
						<div className="space-y-4">
							{cartItems.map((item) => (
								<div key={item.id} className="flex items-center gap-4 p-4 border rounded-lg">
									<div className="text-3xl">{item.image}</div>
									<div className="flex-1">
										<h3 className="font-medium">{item.name}</h3>
										<p className="text-sm text-gray-500">${item.price.toFixed(2)} each</p>
									</div>
									<div className="flex items-center gap-2">
										<Button
											variant="outline"
											size="icon"
											className="h-8 w-8"
											onClick={() => updateQuantity(item.id, item.quantity - 1)}
										>
											<Minus className="w-3 h-3" />
										</Button>
										<span className="w-8 text-center text-sm">{item.quantity}</span>
										<Button
											variant="outline"
											size="icon"
											className="h-8 w-8"
											onClick={() => updateQuantity(item.id, item.quantity + 1)}
										>
											<Plus className="w-3 h-3" />
										</Button>
									</div>
									<div className="text-right">
										<p className="font-medium">${(item.price * item.quantity).toFixed(2)}</p>
										<Button
											variant="outline"
											size="sm"
											className="text-red-600 hover:bg-red-50 mt-1"
											onClick={() => removeItem(item.id)}
										>
											<Trash2 className="w-3 h-3" />
										</Button>
									</div>
								</div>
							))}
							
							{/* Order Summary */}
							<div className="border-t pt-4 mt-6">
								<div className="space-y-2">
									<div className="flex justify-between text-sm">
										<span>Subtotal:</span>
										<span>${getTotalPrice().toFixed(2)}</span>
									</div>
									<div className="flex justify-between text-sm">
										<span>Shipping:</span>
										<span>$5.99</span>
									</div>
									<div className="flex justify-between text-sm">
										<span>Tax:</span>
										<span>${(getTotalPrice() * 0.08).toFixed(2)}</span>
									</div>
									<div className="border-t pt-2 flex justify-between font-medium">
										<span>Total:</span>
										<span>${(getTotalPrice() + 5.99 + (getTotalPrice() * 0.08)).toFixed(2)}</span>
									</div>
								</div>
							</div>

							{/* Promo Code */}
							<div className="border-t pt-4">
								<div className="flex gap-2">
									<Input placeholder="Promo code" className="flex-1" />
									<Button variant="outline">Apply</Button>
								</div>
							</div>
						</div>
					)}
				</DrawerBody>
				<DrawerFooter className="grid-cols-2">
					<DrawerClose asChild>
						<Button variant="outline" className="w-full">
							Continue Shopping
						</Button>
					</DrawerClose>
					<Button 
						className="w-full"
						disabled={cartItems.length === 0}
						onClick={() => alert('Proceeding to checkout...')}
					>
						Checkout (${(getTotalPrice() + 5.99 + (getTotalPrice() * 0.08)).toFixed(2)})
					</Button>
				</DrawerFooter>
			</DrawerContent>
		</Drawer>
	);
}
```

Copy-paste these files for dependencies:
```tsx
shadcn/button
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive:
          "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline:
          "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  },
)
Button.displayName = "Button"

export { Button, buttonVariants }

```
```tsx
shadcn/input
import * as React from "react"

import { cn } from "@/lib/utils"

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }

```

Install NPM dependencies:
```bash
vaul, @radix-ui/react-slot, class-variance-authority
```

Implementation Guidelines
 1. Analyze the component structure and identify all required dependencies
 2. Review the component's argumens and state
 3. Identify any required context providers or hooks and install them
 4. Questions to Ask
 - What data/props will be passed to this component?
 - Are there any specific state management requirements?
 - Are there any required assets (images, icons, etc.)?
 - What is the expected responsive behavior?
 - What is the best place to use this component in the app?

Steps to integrate
 0. Copy paste all the code above in the correct directories
 1. Install external dependencies
 2. Fill image assets with Unsplash stock images you know exist
 3. Use lucide-react icons for svgs or logos if component requires them

