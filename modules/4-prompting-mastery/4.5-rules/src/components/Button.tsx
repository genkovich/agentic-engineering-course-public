import "../styles/button.css";

export type ButtonVariant = "primary" | "secondary" | "ghost";

export interface ButtonProps {
  variant?: ButtonVariant;
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

export default function Button({
  variant = "primary",
  disabled = false,
  onClick,
  children,
}: ButtonProps) {
  return (
    <button
      type="button"
      className={`button button--${variant}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
