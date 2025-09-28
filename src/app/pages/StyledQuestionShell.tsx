"use client";

import React from "react";
import styled from "styled-components";

type Props = {
  step: number;
  total: number;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  onBack?: () => void;
  onNext?: () => void;
  nextDisabled?: boolean;
  onStepSelect?: (step: number) => void;
};

const Root = styled.div`
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff2e4; /* orange-50 tone */
`;

const Frame = styled.div`
  width: 1318px;
  max-width: calc(100% - 48px);
  height: 720px;
  max-height: calc(100vh - 48px);
  background: white;
  border-radius: 15px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
`;

const HeaderStack = styled.div`
  position: absolute;
  left: 454px;
  top: 144px;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  text-align: center;
`;

const Title = styled.div`
  color: #26203b;
  font-size: 24px;
  font-family: Inter, ui-sans-serif, system-ui;
  font-weight: 500;
`;

const SubTitle = styled.div`
  color: #9c9aa5;
  font-size: 18px;
  font-family: Inter, ui-sans-serif, system-ui;
`;

const Brand = styled.div`
  position: absolute;
  left: 582px;
  top: 52px;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const BrandMark = styled.div`
  width: 36px;
  height: 31px;
  background: #ff901c; /* amber */
  border-radius: 4px;
`;

const BrandName = styled.div`
  color: #ff901c;
  font-size: 16px;
  font-family: Sarala, Inter, ui-sans-serif, system-ui;
  font-weight: 700;
  letter-spacing: 1.2px;
`;

const Card = styled.div`
  position: absolute;
  left: 467px;
  top: 238px;
  width: 383px;
  max-width: calc(100% - 64px);
  background: #fff;
  border-radius: 8px;
  outline: 1px #e8eaed solid;
  padding: 16px;
`;

const NextButton = styled.button<{ disabled?: boolean }>`
  position: absolute;
  left: 580px;
  top: 590px;
  width: 158px;
  height: 36px;
  border-radius: 6px;
  border: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: ${(p) => (p.disabled ? "#FDBA74" : "#FF901C")};
  color: #fff;
  font-weight: 700;
  cursor: ${(p) => (p.disabled ? "not-allowed" : "pointer")};
`;

const Footer = styled.div`
  position: absolute;
  left: 24px;
  right: 24px;
  bottom: 16px;
  display: flex;
  width: calc(100% - 48px);
  justify-content: space-between;
  color: #9c9aa5;
  font-size: 12px;
`;

const Progress = styled.div`
  position: absolute;
  left: 610px;
  top: 558px;
  color: #9c9aa5;
  font-size: 13.5px;
  font-weight: 500;
  text-transform: uppercase;
`;

const ProgressDots = styled.div`
  position: absolute;
  left: 0;
  right: 0;
  bottom: 72px;
  display: flex;
  gap: 8px;
  justify-content: center;
`;

const Dot = styled.button<{ active?: boolean; done?: boolean }>`
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: none;
  background: ${({ active, done }) =>
    active ? "#FF901C" : done ? "#00D149" : "#D8DADF"};
`;

export default function StyledQuestionShell({
  step,
  total,
  title,
  subtitle,
  children,
  onBack,
  onNext,
  nextDisabled,
  onStepSelect,
}: Props) {
  return (
    <Root>
      <Frame>
        <Brand>
          <BrandMark />
          <BrandName>Medigator</BrandName>
        </Brand>

        <HeaderStack>
          <Title>{title}</Title>
          {subtitle && <SubTitle>{subtitle}</SubTitle>}
        </HeaderStack>

        <Card>{children}</Card>

        {onNext && (
          <NextButton onClick={onNext} disabled={!!nextDisabled}>
            Next
          </NextButton>
        )}

        <Progress>
          {step} / {total}
        </Progress>

        <ProgressDots>
          {Array.from({ length: total }).map((_, i) => {
            const s = i + 1;
            const active = s === step;
            const done = s < step;
            return (
              <Dot
                key={s}
                active={active}
                done={done}
                onClick={() => onStepSelect?.(s)}
                title={`Step ${s}`}
              />
            );
          })}
        </ProgressDots>

        <Footer>
          <span>© 2025 Medigator. All rights reserved.</span>
          <span>Demo only — Not diagnostic • No PHI.</span>
        </Footer>
      </Frame>
    </Root>
  );
}
