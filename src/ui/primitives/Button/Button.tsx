import { clsx } from "clsx";
import React, { ComponentPropsWithoutRef } from "react";
import { Button as RACButton, Link as RACLink } from "react-aria-components";
import { type AnchorOrButtonProps } from "utils";
import "./button.css";

export type ButtonProps = Omit<ButtonBaseProps, "variant"> & {
  variant?: Exclude<
    ButtonBaseProps["variant"],
    "danger-primary" | "danger-subtle" | "success-primary" | "success-subtle"
  >;
};
export const Button = React.forwardRef(function Button(
  { className, size = "medium", variant = "primary", ...props }: ButtonProps,
  ref: React.ForwardedRef<HTMLElement>,
) {
  const classNames = clsx(
    className,
    "button",
    `button-size-${size}`,
    `button-variant-${variant}`,
  );

  if (isAnchorProps(props)) {
    const { style, ...anchorProps } = props;
    return (
      <RACLink
        {...anchorProps}
        className={classNames}
        ref={ref as React.ForwardedRef<HTMLAnchorElement>}
      >
        {props.children}
      </RACLink>
    );
  }

  const { style, ...buttonProps } = props;
  return (
    <RACButton
      {...(buttonProps as ComponentPropsWithoutRef<typeof RACButton>)}
      className={classNames}
      ref={ref as React.ForwardedRef<HTMLButtonElement>}
    >
      {props.children}
    </RACButton>
  );
});

export type ButtonDangerProps = Omit<ButtonBaseProps, "variant"> & {
  variant?: Exclude<
    ButtonBaseProps["variant"],
    "primary" | "subtle" | "neutral" | "success-primary" | "success-subtle"
  >;
};
/**
 * Only used for destructive actions
 */
export const ButtonDanger = React.forwardRef(function Button(
  {
    className,
    size = "medium",
    variant = "danger-primary",
    ...props
  }: ButtonDangerProps,
  ref: React.ForwardedRef<HTMLElement>,
) {
  const classNames = clsx(
    className,
    "button",
    `button-size-${size}`,
    `button-variant-${variant}`,
  );

  if (isAnchorProps(props)) {
    const { style, ...anchorProps } = props;
    return (
      <RACLink
        {...anchorProps}
        className={classNames}
        ref={ref as React.ForwardedRef<HTMLAnchorElement>}
      >
        {props.children}
      </RACLink>
    );
  }

  const { style, ...buttonProps } = props;
  return (
    <RACButton
      {...(buttonProps as ComponentPropsWithoutRef<typeof RACButton>)}
      className={classNames}
      ref={ref as React.ForwardedRef<HTMLButtonElement>}
    >
      {props.children}
    </RACButton>
  );
});

export type ButtonSuccessProps = Omit<ButtonBaseProps, "variant"> & {
  variant?: Exclude<
    ButtonBaseProps["variant"],
    "primary" | "subtle" | "neutral" | "danger-primary" | "danger-subtle"
  >;
};
/**
 * Only used for positive, confirming actions
 */
export const ButtonSuccess = React.forwardRef(function Button(
  {
    className,
    size = "medium",
    variant = "success-primary",
    ...props
  }: ButtonSuccessProps,
  ref: React.ForwardedRef<HTMLElement>,
) {
  const classNames = clsx(
    className,
    "button",
    `button-size-${size}`,
    `button-variant-${variant}`,
  );

  if (isAnchorProps(props)) {
    const { style, ...anchorProps } = props;
    return (
      <RACLink
        {...anchorProps}
        className={classNames}
        ref={ref as React.ForwardedRef<HTMLAnchorElement>}
      >
        {props.children}
      </RACLink>
    );
  }

  const { style, ...buttonProps } = props;
  return (
    <RACButton
      {...(buttonProps as ComponentPropsWithoutRef<typeof RACButton>)}
      className={classNames}
      ref={ref as React.ForwardedRef<HTMLButtonElement>}
    >
      {props.children}
    </RACButton>
  );
});

type ButtonBaseProps = {
  type?: ComponentPropsWithoutRef<"button">["type"];
  size?: "small" | "medium";
  variant?:
    | "primary"
    | "neutral"
    | "subtle"
    | "danger-primary"
    | "danger-subtle"
    | "success-primary"
    | "success-subtle";
} & AnchorOrButtonProps;

function isAnchorProps(
  props: ButtonBaseProps | ButtonDangerProps | ButtonSuccessProps,
): props is (ButtonBaseProps | ButtonDangerProps | ButtonSuccessProps) &
  ComponentPropsWithoutRef<typeof RACLink> {
  return "href" in props;
}

export type ButtonGroupProps = React.ComponentPropsWithoutRef<"div"> & {
  align?: "start" | "end" | "center" | "justify" | "stack";
};
export const ButtonGroup = ({
  align = "start",
  className,
  ...props
}: ButtonGroupProps) => {
  const classNames = clsx(
    className,
    "button-group",
    `button-group-align-${align}`,
  );
  return <div className={classNames} {...props} />;
};
