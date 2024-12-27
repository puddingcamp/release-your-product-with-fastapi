import { forwardRef } from "react";
import clsx from "clsx";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant: "primary" | "secondary";
    className?: string;
    children: React.ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    ({ variant, className, children, ...props }, ref) => {
        const variantStyles = {
            primary: "bg-blue-500 text-white",
            secondary: "bg-gray-200 text-gray-800",
        }[variant];

        return (
            <button
                ref={ref}
                className={clsx("rounded-md border border-gray-200", variantStyles, className)}
                {...props}
            >
                {children}
            </button>
        );
    }
);

Button.displayName = 'Button';

export default Button;
