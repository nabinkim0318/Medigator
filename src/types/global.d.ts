// Global type declarations
declare module 'diff' {
  export interface Change {
    value: string;
    added?: boolean;
    removed?: boolean;
  }

  export function diffWords(oldStr: string, newStr: string): Change[];
  export function diffLines(oldStr: string, newStr: string): Change[];
}

declare module 'cmdk' {
  export * from 'cmdk';
}

declare module '@radix-ui/react-dialog' {
  export * from '@radix-ui/react-dialog';
}
