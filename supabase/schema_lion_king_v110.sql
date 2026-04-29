-- LionKing V110 Supabase schema
-- Paste this file into Supabase SQL Editor before running GitHub Actions.

create table if not exists public.lion_king_signals (
  id text primary key,
  name text not null,
  sector text,
  price double precision,
  ma20 double precision,
  macd_hist double precision,
  rsi double precision,
  volume double precision,
  instruction text,
  source_module text default 'update_data.py',
  updated_at timestamp with time zone not null default now()
);

alter table public.lion_king_signals
  add column if not exists sector text,
  add column if not exists macd_hist double precision,
  add column if not exists rsi double precision,
  add column if not exists volume double precision,
  add column if not exists source_module text default 'update_data.py';

create or replace function public.set_lion_king_signals_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_lion_king_signals_updated_at on public.lion_king_signals;

create trigger trg_lion_king_signals_updated_at
before update on public.lion_king_signals
for each row
execute function public.set_lion_king_signals_updated_at();

create table if not exists public.lion_king_strategy_modules (
  module_key text primary key,
  title text not null,
  repo_path text,
  module_type text,
  description text,
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now()
);

create table if not exists public.lion_king_reference_assets (
  asset_key text primary key,
  title text not null,
  asset_type text not null,
  repo_path text,
  local_source text,
  notes text,
  created_at timestamp with time zone not null default now()
);

insert into public.lion_king_strategy_modules (module_key, title, repo_path, module_type, description)
values
  ('realtime_war_room', '即時戰情室', 'colab/即時戰情室.py', 'colab_python', 'V110 Gradio 即時戰情室與全板塊掃描模組'),
  ('smart_index_reader', '智能判讀指數', 'colab/智能判讀指數.py', 'colab_python', 'V105 00631L 與台積電大盤紅綠燈判讀模組'),
  ('smart_stock_picker', '智能選股', 'colab/智能選股.py', 'colab_python', 'V81.4 量價籌碼選股與持倉管理模組'),
  ('automation_war_module', '自動化戰情模組', 'colab/自動化戰情模組.py', 'colab_python', 'V108 全矩陣自動化戰情報告模組')
on conflict (module_key) do update set
  title = excluded.title,
  repo_path = excluded.repo_path,
  module_type = excluded.module_type,
  description = excluded.description,
  updated_at = now();

insert into public.lion_king_reference_assets (asset_key, title, asset_type, repo_path, local_source, notes)
values
  ('stock_strategy_reference_pdf', '股票策略分析參考圖', 'pdf', 'references/股票策略分析參考圖.pdf', 'C:/Users/a0983/Downloads/股票策略分析參考圖.pdf', '大型二進位檔需用 git/gh 或 GitHub 網頁上傳'),
  ('realtime_war_room_colab_pdf', '即時戰情室 Colab', 'pdf', 'references/即時戰情室 - Colab.pdf', 'C:/Users/a0983/Downloads/即時戰情室 - Colab.pdf', '大型二進位檔需用 git/gh 或 GitHub 網頁上傳'),
  ('smart_index_colab_pdf', '智能判讀指數 Colab', 'pdf', 'references/智能判讀指數 - Colab.pdf', 'C:/Users/a0983/Downloads/智能判讀指數 - Colab.pdf', '大型二進位檔需用 git/gh 或 GitHub 網頁上傳'),
  ('smart_picker_colab_pdf', '智能選股 Colab', 'pdf', 'references/智能選股 - Colab.pdf', 'C:/Users/a0983/Downloads/智能選股 - Colab.pdf', '大型二進位檔需用 git/gh 或 GitHub 網頁上傳'),
  ('automation_colab_pdf', '自動化戰情模組 Colab', 'pdf', 'references/自動化戰情模組 - Colab.pdf', 'C:/Users/a0983/Downloads/自動化戰情模組 - Colab.pdf', '大型二進位檔需用 git/gh 或 GitHub 網頁上傳'),
  ('stock_reference_1', '股票分析建議參考圖 1', 'jpg', 'references/股票分析建議參考圖(1).JPG', 'C:/Users/a0983/Downloads/股票分析建議參考圖(1).JPG', '參考圖'),
  ('stock_reference_2', '股票分析建議參考圖 2', 'jpg', 'references/股票分析建議參考圖(2).JPG', 'C:/Users/a0983/Downloads/股票分析建議參考圖(2).JPG', '參考圖'),
  ('stock_reference_3', '股票分析建議參考圖 3', 'jpg', 'references/股票分析建議參考圖(3).JPG', 'C:/Users/a0983/Downloads/股票分析建議參考圖(3).JPG', '參考圖'),
  ('stock_reference_4', '股票分析建議參考圖 4', 'jpg', 'references/股票分析建議參考圖(4).jpg', 'C:/Users/a0983/Downloads/股票分析建議參考圖(4).jpg', '參考圖')
on conflict (asset_key) do update set
  title = excluded.title,
  asset_type = excluded.asset_type,
  repo_path = excluded.repo_path,
  local_source = excluded.local_source,
  notes = excluded.notes;

-- Public read policy for the static GitHub Pages frontend.
alter table public.lion_king_signals enable row level security;

drop policy if exists "Allow public read lion king signals" on public.lion_king_signals;
create policy "Allow public read lion king signals"
on public.lion_king_signals
for select
to anon
using (true);
