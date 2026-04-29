-- LionKing V111 strategy upgrade
-- Paste this file into Supabase SQL Editor after schema_lion_king_v110.sql.
-- It is additive only: existing data is preserved.

alter table public.lion_king_signals
  add column if not exists strategy_score integer,
  add column if not exists signal_level text,
  add column if not exists risk_level text,
  add column if not exists position_plan text,
  add column if not exists entry_zone text,
  add column if not exists support_zone text,
  add column if not exists pressure_zone text,
  add column if not exists stop_loss double precision,
  add column if not exists take_profit double precision,
  add column if not exists strategy_tags text[],
  add column if not exists analysis_note text;

create table if not exists public.lion_king_strategy_rules (
  rule_key text primary key,
  title text not null,
  category text not null,
  condition_text text,
  action_text text,
  weight integer default 0,
  source_title text,
  enabled boolean not null default true,
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now()
);

create or replace function public.set_lion_king_strategy_rules_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_lion_king_strategy_rules_updated_at on public.lion_king_strategy_rules;

create trigger trg_lion_king_strategy_rules_updated_at
before update on public.lion_king_strategy_rules
for each row
execute function public.set_lion_king_strategy_rules_updated_at();

insert into public.lion_king_strategy_rules (rule_key, title, category, condition_text, action_text, weight, source_title)
values
  ('ma20_life_line', '20MA 生命線', '技術面', '收盤價站上 20MA 才允許偏多；跌破 20MA 視為轉弱警訊。', '站穩 20MA 可觀察回檔買點；跌破先降部位或空手等待。', 18, '核心股票技術策略與校正 / 智能選股'),
  ('macd_momentum', 'MACD 動能柱', '技術面', 'MACD histogram 由負轉正或持續擴大，代表短線動能轉強。', '動能轉強且價格在月線上方可列入候選；動能縮小時避免追價。', 14, 'MACD成交量策略標準研擬 / 自動化戰情模組'),
  ('volume_ratio', '估量比與量能放大', '量價', '成交量高於 20 日均量且價格同步站穩均線，訊號可信度提高。', '量增價漲偏多；量增但跌破支撐視為出貨或分歧風險。', 12, '台股估量比策略分析 / 風暴比策略'),
  ('rsi_heat', 'RSI 過熱與過冷', '技術面', 'RSI 高於 78 視為短線過熱，低於 35 視為超跌反彈觀察。', '過熱不追高；超跌必須等價格重新站回關鍵均線。', 10, '智能判讀指數 / 趨勢交易策略深度研究'),
  ('k_three_three', 'K 線三三原則', 'K線型態', '連續三根 K 線守住支撐且高低點墊高，才視為較完整的轉強結構。', '未形成三三結構前只觀察；跌破前低則訊號失效。', 9, 'K線三三原則與進場策略'),
  ('chip_follow', '籌碼主力順風', '籌碼面', '法人或主力買超與股價同步上升，代表籌碼偏順風。', '價漲但籌碼分歧時降低追高權重；連續賣超應守停損。', 13, '籌碼面分析進出場訊號 / 資金流向策略法則'),
  ('risk_stop', '停損停利與部位控管', '風控', '跌破 20MA 或跌破停損線先處理風險；漲幅過大分批停利。', '不攤平破線標的；單一股票避免重壓，分批進出。', 15, '策略模擬器 / 投資訊號與警示深度分析'),
  ('macro_estop', '黑天鵝與宏觀 E-Stop', '宏觀風控', '大盤、台積電、槓桿 ETF 同步轉弱時，系統應切換防守模式。', '降低持股、保留現金、避免逆勢追高；等市場重新轉強再恢復攻擊。', 16, '黑天鵝與宏觀對沖機制 / 中東局勢影響台股訊號判斷')
on conflict (rule_key) do update set
  title = excluded.title,
  category = excluded.category,
  condition_text = excluded.condition_text,
  action_text = excluded.action_text,
  weight = excluded.weight,
  source_title = excluded.source_title,
  updated_at = now();

alter table public.lion_king_strategy_rules enable row level security;

drop policy if exists "Allow public read lion king strategy rules" on public.lion_king_strategy_rules;
create policy "Allow public read lion king strategy rules"
on public.lion_king_strategy_rules
for select
to anon
using (true);
